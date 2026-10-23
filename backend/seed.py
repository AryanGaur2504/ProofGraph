"""Deterministic, fictional SIH demo only. Run: python seed.py --reset"""
import argparse, io, json, shutil
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image, ImageDraw
from sqlalchemy import select
from app.db import create_all,Base,engine,SessionLocal
from app.models import User,Institution,Application,ApplicationSnapshot,Document,ExtractedField,Verification
from app.storage import storage
from app.security import hash_password,encrypt_sensitive
from app.processing import process_bytes
from app.rules import install_rules
from app.engine import validate_case
from app.audit import write_audit

ROOT=Path(__file__).resolve().parent

def pdf(title,values):
    buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=A4,pageCompression=0)
    c.setTitle('SYNTHETIC DEMONSTRATION DOCUMENT - '+title)
    c.setFont('Helvetica-Bold',16);c.drawString(48,790,'PROOFGRAPH · SYNTHETIC DEMONSTRATION DATA')
    c.setFont('Helvetica-Bold',14);c.drawString(48,750,title)
    c.setFont('Helvetica',12);y=704
    for key,value in values.items():
        c.drawString(50,y,f'{key}: {value}');y-=35
    c.setFont('Helvetica',9);c.drawString(48,55,'Not valid as a certificate or official institutional evidence. Demo only.')
    c.save();return buf.getvalue()

def picture():
    im=Image.new('RGB',(900,530),'#e9f2f8');draw=ImageDraw.Draw(im)
    draw.rectangle((40,130,860,495),outline='#0b2545',width=10)
    for i in range(5):
        draw.rectangle((90+i*145,210,170+i*145,385),outline='#13a89e',width=7)
    draw.text((55,55),'SYNTHETIC: INFRASTRUCTURE PHOTO / ROOM A1',fill='#0b2545')
    buf=io.BytesIO();im.save(buf,format='PNG');return buf.getvalue()

def new_doc(db,app,filename,data,kind=None):
    info=process_bytes(data,filename)
    ext=Path(filename).suffix.lower()
    d=Document(application_id=app.id,name=filename,kind=kind or info['kind'],path=storage.write(data,filename),sha256=info['sha256'],perceptual_hash=info['perceptual_hash'],mime='application/pdf' if ext=='.pdf' else 'image/png',metadata_json=info['metadata'])
    db.add(d);db.flush()
    for f in info['fields']:
        db.add(ExtractedField(document_id=d.id,**f))
        if f['key']=='expiry':d.expiry=f['value']
    db.flush();return d

def new_institution(db,name,code):
    ins=Institution(name=name,code=code,address_encrypted=encrypt_sensitive('Synthetic campus address only'))
    db.add(ins);db.flush();return ins

def new_case(db,ins):
    a=Application(institution_id=ins.id,category='Extension of Approval',year=2026,state='Under Scrutiny',submitted=True)
    db.add(a);db.flush();return a

def form(ins,labs,faculty='58',intake='480'):
    return pdf('Application Form',{'Institution Name':ins.name,'Laboratories':labs,'Faculty Count':faculty,'Intake':intake})

def inventory(ins,labs):
    return pdf('Room Inventory',{'Institution Name':ins.name,'Laboratories':labs})

def fire(ins,expiry='2028-12-31'):
    return pdf('Fire Safety Certificate',{'Institution Name':ins.name,'Certificate Number':f'SYN-FIRE-{ins.id:04}','Expiry Date':expiry})

def build(reset=False):
    if reset:
        dburl=str(engine.url)
        if not dburl.startswith('sqlite') or '/proofgraph.db' not in dburl:
            raise RuntimeError('Refusing reset on nonstandard database; use isolated test DB separately')
        Base.metadata.drop_all(bind=engine)
        if storage.root.exists():
            for item in storage.root.iterdir():
                if item.is_file() and item.suffix.lower() in {'.pdf','.png','.jpg','.jpeg','.webp'}:item.unlink()
    create_all()
    with SessionLocal() as db:
        if db.scalars(select(User)).first():
            print('Seed already exists. Run python seed.py --reset for a clean synthetic dataset.');return
        install_rules(db)
        m=new_institution(db,'Meridian Institute of Technology','SYN-MERIDIAN')
        b=new_institution(db,'Blue Ridge Engineering College','SYN-BLUERIDGE')
        c=new_institution(db,'Northstar Technology Institute','SYN-NORTHSTAR')
        for username,role,institution in [('admin','Admin',None),('officer','Scrutiny Officer',None),('senior','Senior Officer',None),('auditor','Auditor',None),('institution','Institution',m.id)]:
            db.add(User(username=username,password_hash=hash_password('Demo@12345'),role=role,institution_id=institution))
        db.flush()
        hero=[]
        first=new_case(db,m)
        new_doc(db,first,'meridian-application.pdf',form(m,'18'))
        new_doc(db,first,'meridian-room-inventory.pdf',inventory(m,'15'))
        new_doc(db,first,'meridian-fire-certificate.pdf',fire(m))
        shared=pdf('Building Certificate',{'Issuer Name':'Synthetic Common Contractor','Certificate Number':'SYN-BUILD-REUSED-0007'})
        new_doc(db,first,'meridian-building.pdf',shared)
        new_doc(db,first,'meridian-room-photo.png',picture(),kind='Infrastructure Photo')
        db.add(ApplicationSnapshot(application_id=first.id,year=2025,fields={'laboratories':'12','faculty_count':'58','intake':'480'}))
        hero.append(first)
        second=new_case(db,b)
        new_doc(db,second,'blueridge-application.pdf',form(b,'10'))
        new_doc(db,second,'blueridge-inventory.pdf',inventory(b,'10'))
        new_doc(db,second,'blueridge-fire-expired.pdf',fire(b,'2024-06-30'))
        new_doc(db,second,'blueridge-building.pdf',shared)
        db.add(ApplicationSnapshot(application_id=second.id,year=2025,fields={'laboratories':'10','faculty_count':'58','intake':'480'}))
        hero.append(second)
        clean=new_case(db,c)
        new_doc(db,clean,'northstar-application.pdf',form(c,'14'))
        new_doc(db,clean,'northstar-inventory.pdf',inventory(c,'14'))
        new_doc(db,clean,'northstar-fire.pdf',fire(c))
        db.add(ApplicationSnapshot(application_id=clean.id,year=2025,fields={'laboratories':'14','faculty_count':'58','intake':'480'}))
        hero.append(clean)
        # Source-unavailable stub never marks anything officially verified.
        db.add(Verification(application_id=second.id,source='SIMULATED DEMO ADAPTER — NO GOVERNMENT CONNECTION',status='SOURCE_UNAVAILABLE',simulated=True,detail='Fixture demonstrates an unresolved external authority query'))
        db.flush()
        for a in hero: validate_case(db,a.id)
        labels=[]
        for i in range(30):
            ins=new_institution(db,f'Synthetic Evaluation College {i+1:02}',f'SYN-EVAL-{i+1:02}')
            a=new_case(db,ins)
            defect=i<24
            declared=str(10+i%7)
            actual=str(int(declared)-2) if i<10 else declared
            expected_docs={}
            name=f'eval-{i+1:02}-application.pdf';new_doc(db,a,name,form(ins,declared));expected_docs[name]='Application Form'
            if not (18<=i<24):
                name=f'eval-{i+1:02}-inventory.pdf';new_doc(db,a,name,inventory(ins,actual));expected_docs[name]='Room Inventory'
            if i<10 or 10<=i<18 or i>=24:
                name=f'eval-{i+1:02}-fire.pdf';new_doc(db,a,name,fire(ins,'2023-01-02' if 10<=i<18 else '2029-01-02'));expected_docs[name]='Fire Safety Certificate'
            # Tests deliberately isolate 6 missing-document cases and 6 clean cases.
            db.flush();validate_case(db,a.id)
            labels.append({'application_id':a.id,'defect':defect,'expected_docs':expected_docs,'expected_fields':{'laboratories':declared}})
        (ROOT/'evaluation_labels.json').write_text(json.dumps(labels,indent=2),encoding='utf-8')
        write_audit(db,None,'SEED_SYNTHETIC_DATA','dataset',after={'hero_cases':[a.id for a in hero],'evaluation_cases':len(labels),'synthetic':True})
        db.commit()
        print('SYNTHETIC DEMONSTRATION DATA seeded:')
        print('Hero IDs:',*[a.id for a in hero])
        print('30 labelled evaluation cases created')
        print('Accounts: admin, officer, senior, auditor, institution | Password: Demo@12345')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--reset',action='store_true',help='Delete existing synthetic demo DB and sample storage; NEVER use on user data')
    args=parser.parse_args();build(reset=args.reset)
