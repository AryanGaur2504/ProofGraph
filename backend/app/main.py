import hashlib, os, json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import get_db, create_all, SessionLocal
from .models import (User,Institution,Application,ApplicationSnapshot,Document,ExtractedField,Claim,Finding,FindingEvidence,Verification,
                     ReviewAction,ChangeRecord,Report,Rule,RuleVersion,AuditEvent)
from .security import check_password,make_token,current_user,require_roles,check_case_access,mask_sensitive,WRITE_ROLES
from .processing import process_bytes,advisory_signals
from .storage import storage
from .rules import install_rules,current_rules,checklist
from .engine import validate_case,graph_json,priority,neighborhood,cross_institution_patterns
from .audit import write_audit,verify_audit
from .reports import build_report
from .evaluation import evaluate
from .verification import SimulatedAdapter, AuthorizedSourceStub, save_outcome
from .llm import DisabledLLM, CaseEvidence

@asynccontextmanager
async def lifespan(_: FastAPI):
    create_all()
    with SessionLocal() as db:
        install_rules(db)
        db.commit()
    yield

app=FastAPI(title='AICTE ProofGraph (Synthetic Prototype)',description='Evidence-linked scrutiny; no official AICTE endorsement; only sample rules.',version='0.9.0',openapi_url='/api/openapi.json',docs_url='/api/docs',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=os.environ.get('PROOFGRAPH_CORS','http://localhost:3000,http://127.0.0.1:3000').split(','),allow_credentials=True,allow_methods=['*'],allow_headers=['*'])

class LoginInput(BaseModel):
    username:str
    password:str
class CreateCase(BaseModel):
    institution_id:int
    category:str='Extension of Approval'
    year:int=2026
class EditField(BaseModel):
    value:str=Field(min_length=1,max_length=1000)
    reason:str=Field(min_length=3)
class ReviewRequest(BaseModel):
    action:Literal['Confirm','Dismiss','Request evidence','Escalate for inspection']
    reason:str=Field(min_length=3)
class RuleUpdate(BaseModel):
    severity:Literal['High','Medium','Low']
    specification:dict
    source_citation:str=Field(min_length=5)
    effective_from:str
class AskRequest(BaseModel):
    question:str=Field(min_length=3,max_length=600)

def app_get(db,u,id): return check_case_access(db,u,db.get(Application,id))
def doc_get(db,u,id):
    d=db.get(Document,id)
    if not d: raise HTTPException(404,'No document')
    app_get(db,u,d.application_id)
    return d

def serialize_finding(f):
    return {'id':f.id,'title':f.title,'category':f.category,'severity':f.severity,'reason':f.reason,'next_action':f.next_action,'rule_id':f.rule_id,'rule_version':f.rule_version,'source_a':f.source_a,'source_b':f.source_b,'official_status':f.official_status,'consistency_status':f.consistency_status,'ai_status':f.ai_status,'manual_status':f.manual_status}

def serialize_case(db,a,user):
    ins=db.get(Institution,a.institution_id)
    docs=db.scalars(select(Document).where(Document.application_id==a.id)).all()
    findings=db.scalars(select(Finding).where(Finding.application_id==a.id)).all()
    findings.sort(key=lambda f:({'High':0,'Medium':1,'Low':2}.get(f.severity,3),0 if 'Laboratories conflict' in f.title else 1,f.id))
    changes=db.scalars(select(ChangeRecord).where(ChangeRecord.application_id==a.id)).all()
    vers=db.scalars(select(Verification).where(Verification.application_id==a.id)).all()
    reviews=db.scalars(select(ReviewAction).join(Finding,ReviewAction.finding_id==Finding.id).where(Finding.application_id==a.id)).all()
    snapshots=db.scalars(select(ApplicationSnapshot).where(ApplicationSnapshot.application_id==a.id)).all()
    required=checklist(db,a.category)
    if user.role=='Institution':
        # Institution accounts may review a pattern signal but must never read another institution's underlying document.
        finding_payload=[]
        own_doc_ids={d.id for d in docs}
        for finding in findings:
            item=serialize_finding(finding)
            for side in ('source_a','source_b'):
                source=item[side] or {}
                if source.get('document_id') and source['document_id'] not in own_doc_ids:
                    item[side]={'document_id':None,'document_name':'Other institution · restricted','page':None,'bbox':[],
                                'field':source.get('field'),'value':'RESTRICTED · officer review only'}
            finding_payload.append(item)
    else:
        finding_payload=[serialize_finding(f) for f in findings]
    return {'id':a.id,'institution':ins.name,'institution_id':ins.id,'institution_code':ins.code,'address':mask_sensitive(ins.address_encrypted or '',user.role),'category':a.category,'year':a.year,'state':a.state,'submitted':a.submitted,'synthetic':True,
            'priority':priority(findings),'checklist':[{'type':k,'present':any(d.kind==k for d in docs),'expired':any(d.kind==k and d.expiry and d.expiry<datetime.now(timezone.utc).date().isoformat() for d in docs)} for k in required],
            'documents':[{'id':d.id,'name':d.name,'kind':d.kind,'mime':d.mime,'sha256':d.sha256,'perceptual_hash':d.perceptual_hash,'expiry':d.expiry,'processing_status':d.processing_status,'metadata':d.metadata_json,'fields':[{'id':f.id,'key':f.key,'value':f.value,'confidence':f.confidence,'page':f.page,'bbox':f.bbox,'corrected':f.corrected} for f in db.scalars(select(ExtractedField).where(ExtractedField.document_id==d.id))]} for d in docs],
            'findings':finding_payload,
            'changes':[{'key':c.key,'old_value':c.old_value,'new_value':c.new_value,'explained':c.explained,'evidence_required':c.evidence_required,'explanation':c.explanation} for c in changes],
            'snapshots':[{'year':s.year,'fields':s.fields} for s in snapshots],
            'verifications':[{'id':v.id,'document_id':v.document_id,'source':v.source,'status':v.status,'simulated':v.simulated,'detail':v.detail} for v in vers],
            'review_actions':[{'id':r.id,'finding_id':r.finding_id,'action':r.action,'reason':r.reason,'user_id':r.user_id,'at':r.created_at.isoformat()} for r in reviews]}

@app.get('/api/health')
def health(): return {'status':'ok','prototype':True,'data':'SYNTHETIC DEMONSTRATION DATA'}
@app.post('/api/auth/login')
def login(body:LoginInput,db:Session=Depends(get_db)):
    user=db.scalars(select(User).where(User.username==body.username)).first()
    if not user or not check_password(body.password,user.password_hash): raise HTTPException(401,'Invalid demo credentials')
    return {'access_token':make_token(user),'user':{'id':user.id,'username':user.username,'role':user.role,'institution_id':user.institution_id}}
@app.get('/api/auth/me')
def me(user:User=Depends(current_user)): return {'id':user.id,'username':user.username,'role':user.role,'institution_id':user.institution_id}

@app.get('/api/institutions')
def institutions(db:Session=Depends(get_db),user:User=Depends(current_user)):
    return [{'id':x.id,'name':x.name,'code':x.code} for x in db.scalars(select(Institution)) if user.role!='Institution' or user.institution_id==x.id]

@app.get('/api/cases')
def cases(state:str|None=None,category:str|None=None,severity:str|None=None,unexplained_only:bool=False,db:Session=Depends(get_db),user:User=Depends(current_user)):
    apps=db.scalars(select(Application).order_by(Application.id)).all();result=[]
    for a in apps:
        if user.role=='Institution' and a.institution_id!=user.institution_id: continue
        if state and a.state!=state: continue
        if category and a.category!=category: continue
        findings=db.scalars(select(Finding).where(Finding.application_id==a.id,Finding.manual_status!='SUPERSEDED')).all()
        if severity and not any(f.severity==severity for f in findings): continue
        if unexplained_only and not db.scalars(select(ChangeRecord).where(ChangeRecord.application_id==a.id,ChangeRecord.explained==False)).first(): continue
        ins=db.get(Institution,a.institution_id)
        result.append({'id':a.id,'institution':ins.name,'institution_code':ins.code,'category':a.category,'year':a.year,'state':a.state,'findings_count':len(findings),'priority':priority(findings),'unexplained_count':len(db.scalars(select(ChangeRecord).where(ChangeRecord.application_id==a.id,ChangeRecord.explained==False)).all())})
    return result
@app.post('/api/cases')
def create_case(body:CreateCase,db:Session=Depends(get_db),user:User=Depends(current_user)):
    if user.role!='Institution' and user.role not in WRITE_ROLES:raise HTTPException(403,'Insufficient permissions')
    if user.role=='Institution' and body.institution_id!=user.institution_id:raise HTTPException(403,'Only your institution')
    if not db.get(Institution,body.institution_id):raise HTTPException(404,'Institution not found')
    app_obj=Application(institution_id=body.institution_id,category=body.category,year=body.year,state='Draft',submitted=False)
    db.add(app_obj);db.flush();write_audit(db,user.id,'CREATE_CASE',f'application:{app_obj.id}',after=body.model_dump());db.commit()
    return {'id':app_obj.id}
@app.get('/api/cases/{case_id}')
def case_detail(case_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    return serialize_case(db,app_get(db,user,case_id),user)
@app.post('/api/cases/{case_id}/submit')
def submit_case(case_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    a=app_get(db,user,case_id)
    if user.role!='Institution':raise HTTPException(403,'Only institutions submit cases')
    old=a.state;a.submitted=True;a.state='Submitted'
    write_audit(db,user.id,'SUBMIT_CASE',f'application:{case_id}',before={'state':old},after={'state':a.state});db.commit()
    return {'state':a.state}

@app.post('/api/cases/{case_id}/documents')
async def upload(case_id:int,file:UploadFile=File(...),kind:str|None=Form(None),db:Session=Depends(get_db),user:User=Depends(current_user)):
    a=app_get(db,user,case_id)
    if user.role not in WRITE_ROLES|{'Institution'}:raise HTTPException(403,'Read-only role')
    if user.role=='Institution' and a.submitted:raise HTTPException(403,'Submitted evidence can only be amended by officers; request a revision')
    if not file.filename:raise HTTPException(400,'Filename is required')
    raw=await file.read(20*1024*1024+1)
    if len(raw)>20*1024*1024:raise HTTPException(413,'Maximum upload is 20MB')
    if not raw:raise HTTPException(400,'Empty file')
    ext=Path(file.filename).suffix.lower()
    if ext=='.pdf' and not raw.startswith(b'%PDF'):raise HTTPException(415,'Invalid PDF signature')
    if ext not in {'.pdf','.png','.jpg','.jpeg','.webp'}:raise HTTPException(415,'Unsupported file')
    try: processing=process_bytes(raw,file.filename)
    except Exception as exc:raise HTTPException(422,'Document could not be parsed') from exc
    saved=storage.write(raw,file.filename)
    doc=Document(application_id=case_id,kind=kind or processing['kind'],name=Path(file.filename).name[:240],path=saved,mime='application/pdf' if ext=='.pdf' else 'image/'+ext.lstrip('.'),sha256=processing['sha256'],perceptual_hash=processing['perceptual_hash'],metadata_json=processing['metadata'])
    db.add(doc);db.flush()
    for entry in processing['fields']:
        db.add(ExtractedField(document_id=doc.id,**entry))
        if entry['key']=='expiry':doc.expiry=entry['value']
    db.flush();validate_case(db,case_id)
    write_audit(db,user.id,'UPLOAD_DOCUMENT',f'document:{doc.id}',after={'name':doc.name,'sha256':doc.sha256,'kind':doc.kind});db.commit()
    return {'id':doc.id,'kind':doc.kind,'fields_found':len(processing['fields']),'processing_status':'complete','advisory_only':True}
@app.get('/api/documents/{document_id}/metadata')
def doc_metadata(document_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    d=doc_get(db,user,document_id)
    return {'id':d.id,'name':d.name,'kind':d.kind,'mime':d.mime,'expiry':d.expiry,'fields':[{'id':f.id,'key':f.key,'value':f.value,'page':f.page,'bbox':f.bbox,'confidence':f.confidence,'corrected':f.corrected} for f in db.scalars(select(ExtractedField).where(ExtractedField.document_id==d.id))]}

@app.get('/api/documents/{document_id}/file')
def view_file(document_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    d=doc_get(db,user,document_id)
    return Response(storage.read(d.path),media_type=d.mime,headers={'Content-Disposition':f'inline; filename="{Path(d.name).name}"','Cache-Control':'no-store'})
@app.get('/api/documents/{document_id}/signals')
def signals(document_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    d=doc_get(db,user,document_id)
    return {'document_id':d.id,'signals':advisory_signals(d,storage.read(d.path)),'disclaimer':'Advisory only. Request further evidence or physical inspection.'}
@app.patch('/api/fields/{field_id}')
def patch_field(field_id:int,payload:EditField,db:Session=Depends(get_db),user:User=Depends(current_user)):
    if user.role not in WRITE_ROLES|{'Institution'}:raise HTTPException(403,'Read-only')
    f=db.get(ExtractedField,field_id)
    if not f:raise HTTPException(404,'Field not found')
    d=doc_get(db,user,f.document_id)
    if user.role=='Institution' and db.get(Application,d.application_id).submitted:raise HTTPException(403,'Submitted extraction corrections require officer review')
    old=f.value;f.value=payload.value;f.corrected=True;f.confidence=1.0
    if f.key=='expiry':d.expiry=f.value
    write_audit(db,user.id,'CORRECT_EXTRACTED_FIELD',f'field:{field_id}',before={'value':old},after={'value':f.value,'reason':payload.reason})
    validate_case(db,d.application_id);db.commit();return {'id':f.id,'value':f.value}
@app.post('/api/cases/{case_id}/revalidate')
def revalidate(case_id:int,db:Session=Depends(get_db),user:User=Depends(require_roles('Scrutiny Officer','Senior Officer','Admin'))):
    app_get(db,user,case_id);out=validate_case(db,case_id)
    write_audit(db,user.id,'REVALIDATE_CASE',f'application:{case_id}',after=out);db.commit();return out
@app.get('/api/cases/{case_id}/patterns')
def case_patterns(case_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    app_get(db,user,case_id)
    if user.role=='Institution':return {'patterns':[], 'notice':'Cross-institution records are restricted to authorized officers'}
    return {'patterns':cross_institution_patterns(db,case_id),'notice':'Advisory pattern, not proof of forgery'}

@app.get('/api/cases/{case_id}/graph')
def graph(case_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    app_get(db,user,case_id)
    graph_data=graph_json(db,case_id)
    if user.role=='Institution':
        hidden={n['id'] for n in graph_data['nodes'] if n.get('data',{}).get('external_to_case')}
        graph_data['nodes']=[n for n in graph_data['nodes'] if n['id'] not in hidden]
        graph_data['edges']=[e for e in graph_data['edges'] if e['source'] not in hidden and e['target'] not in hidden]
    return graph_data
@app.get('/api/cases/{case_id}/graph/{node_id}/neighborhood')
def graph_neighbors(case_id:int,node_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    app_get(db,user,case_id);return {'node_ids':neighborhood(db,node_id)}
@app.post('/api/findings/{finding_id}/review')
def review(finding_id:int,payload:ReviewRequest,db:Session=Depends(get_db),user:User=Depends(require_roles('Scrutiny Officer','Senior Officer','Admin'))):
    f=db.get(Finding,finding_id)
    if not f:raise HTTPException(404,'Finding not found')
    old=f.manual_status
    f.manual_status={'Confirm':'CONFIRMED_BY_OFFICER','Dismiss':'DISMISSED_WITH_REASON','Request evidence':'EVIDENCE_REQUESTED','Escalate for inspection':'ESCALATED_FOR_INSPECTION'}[payload.action]
    db.add(ReviewAction(finding_id=f.id,user_id=user.id,action=payload.action,reason=payload.reason))
    write_audit(db,user.id,'REVIEW_FINDING',f'finding:{f.id}',before={'status':old},after={'status':f.manual_status,'reason':payload.reason});db.commit()
    return {'status':f.manual_status,'decision_is_human':True}
@app.post('/api/cases/{case_id}/bulk-request-evidence')
def bulk_request(case_id:int,ids:list[int]=Body(...),db:Session=Depends(get_db),user:User=Depends(require_roles('Scrutiny Officer','Senior Officer','Admin'))):
    app_get(db,user,case_id);count=0
    for item in ids:
        f=db.get(Finding,item)
        if f and f.application_id==case_id and f.manual_status!='SUPERSEDED':
            f.manual_status='EVIDENCE_REQUESTED';db.add(ReviewAction(finding_id=f.id,user_id=user.id,action='Request evidence',reason='Bulk request - officer initiated'));count+=1
    write_audit(db,user.id,'BULK_REQUEST_EVIDENCE',f'application:{case_id}',after={'count':count,'finding_ids':ids});db.commit()
    return {'updated':count}
@app.post('/api/cases/{case_id}/verification/simulate')
def simulate(case_id:int,document_id:int|None=None,status:Literal['PENDING','SOURCE_UNAVAILABLE','MANUAL_REQUIRED']='SOURCE_UNAVAILABLE',db:Session=Depends(get_db),user:User=Depends(require_roles('Scrutiny Officer','Senior Officer','Admin'))):
    app_get(db,user,case_id)
    if document_id:
        d=doc_get(db,user,document_id)
        if d.application_id!=case_id:raise HTTPException(400,'Document not in case')
    v=save_outcome(db,case_id,document_id,SimulatedAdapter(status).verify(document_id))
    write_audit(db,user.id,'SIMULATED_VERIFICATION',f'application:{case_id}',after={'status':status,'simulated':True});db.commit()
    return {'status':v.status,'simulated':True,'officially_verified':False}
@app.get('/api/rules')
def list_rules(db:Session=Depends(get_db),user:User=Depends(current_user)):
    return {'label':'SAMPLE / DEMO RULES — replace only after AICTE handbook review','rules':current_rules(db),'categories':__import__('app.rules',fromlist=['sample_pack']).sample_pack()['categories']}
@app.post('/api/rules/{rule_id}/version')
def update_rule(rule_id:str,payload:RuleUpdate,db:Session=Depends(get_db),user:User=Depends(require_roles('Admin','Senior Officer'))):
    rule=db.scalars(select(Rule).where(Rule.rule_id==rule_id)).first()
    if not rule:raise HTTPException(404,'Rule not found')
    versions=db.scalars(select(RuleVersion).where(RuleVersion.rule_id==rule.id).order_by(RuleVersion.version.desc())).all()
    newest=versions[0]
    ver=RuleVersion(rule_id=rule.id,version=newest.version+1,effective_from=payload.effective_from,severity=payload.severity,specification=payload.specification,source_citation='SAMPLE / DEMO RULE — '+payload.source_citation)
    db.add(ver);write_audit(db,user.id,'RULE_VERSION_CREATED',f'rule:{rule_id}',before={'version':newest.version},after={'version':ver.version,'specification':payload.specification});db.commit()
    return {'rule_id':rule_id,'version':ver.version,'old_versions_preserved':True}
@app.get('/api/audit')
def audits(limit:int=80,db:Session=Depends(get_db),user:User=Depends(require_roles('Scrutiny Officer','Senior Officer','Admin','Auditor'))):
    records=db.scalars(select(AuditEvent).order_by(AuditEvent.id.desc()).limit(min(limit,500))).all()
    return [{'id':r.id,'user_id':r.user_id,'action':r.action,'entity':r.entity,'before':r.before,'after':r.after,'at':r.created_at.isoformat(),'hash':r.hash,'prev_hash':r.prev_hash} for r in records]
@app.get('/api/audit/verify')
def check_audit(db:Session=Depends(get_db),user:User=Depends(require_roles('Scrutiny Officer','Senior Officer','Admin','Auditor'))):return verify_audit(db)
@app.get('/api/evaluation')
def evaluation(db:Session=Depends(get_db),user:User=Depends(require_roles('Scrutiny Officer','Senior Officer','Admin','Auditor'))):return evaluate(db)
@app.post('/api/cases/{case_id}/verification/manual-pending')
def manual_verification(case_id:int,db:Session=Depends(get_db),user:User=Depends(require_roles('Scrutiny Officer','Senior Officer','Admin'))):
    app_get(db,user,case_id)
    v=save_outcome(db,case_id,None,AuthorizedSourceStub().verify())
    write_audit(db,user.id,'VERIFICATION_NOT_CONFIGURED',f'application:{case_id}',after={'status':v.status,'simulated':False});db.commit()
    return {'status':v.status,'simulated':False,'officially_verified':False}

@app.get('/api/cases/{case_id}/ask')
def ask_case_disabled(case_id:int,question:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    a=app_get(db,user,case_id)
    active=[f for f in db.scalars(select(Finding).where(Finding.application_id==case_id)) if f.manual_status!='SUPERSEDED']
    words=set(question.lower().split())
    matches=[f for f in active if words & set((f.title+' '+f.reason).lower().split())]
    if not matches:return {'answer':'Insufficient cited evidence in this case. Ask about an existing finding or review the source documents.','citations':[],'mode':'LOCAL EVIDENCE ONLY · LLM OFF'}
    results=matches[:3]
    grounded=[CaseEvidence(f.title,f.reason,f.next_action,f.source_a,f.source_b,f.rule_id,f.rule_version) for f in results]
    return {'answer':DisabledLLM().explain(question,grounded),'citations':[{'rule_id':f.rule_id,'version':f.rule_version,'source_a':f.source_a,'source_b':f.source_b} for f in results],'mode':'LOCAL EVIDENCE ONLY · LLM OFF'}
@app.post('/api/cases/{case_id}/reports')
def create_report(case_id:int,kind:Literal['evidence','deficiency']='evidence',db:Session=Depends(get_db),user:User=Depends(require_roles('Scrutiny Officer','Senior Officer','Admin'))):
    a=app_get(db,user,case_id);payload=serialize_case(db,a,user);pdf=build_report(payload,kind)
    path=storage.write(pdf,f'{kind}.pdf')
    report=Report(application_id=case_id,path=path,kind=kind,approved_by=None)
    db.add(report);db.flush();write_audit(db,user.id,'GENERATE_DRAFT_REPORT',f'report:{report.id}',after={'kind':kind,'approved':False});db.commit()
    return {'report_id':report.id,'url':f'/api/reports/{report.id}/file','draft':True,'approval_required':True}
@app.post('/api/reports/{report_id}/approve')
def approve_report(report_id:int,db:Session=Depends(get_db),user:User=Depends(require_roles('Senior Officer','Admin'))):
    report=db.get(Report,report_id)
    if not report:raise HTTPException(404,'No report')
    case_data=serialize_case(db,db.get(Application,report.application_id),user)
    old_path=report.path
    report.path=storage.write(build_report(case_data,report.kind,approved=True),'approved.pdf')
    report.approved_by=user.id;write_audit(db,user.id,'APPROVE_REPORT',f'report:{report_id}',before={'old_draft_file':old_path},after={'approved_by':user.id,'new_release_file':report.path,'not_official':True});db.commit()
    return {'approved':True,'approved_by':user.id,'note':'Prototype approval workflow; not legal AICTE issuance'}
@app.get('/api/reports/{report_id}/file')
def download_report(report_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    report=db.get(Report,report_id)
    if not report:raise HTTPException(404,'No report')
    app_get(db,user,report.application_id)
    if user.role=='Institution' and report.approved_by is None:raise HTTPException(403,'Draft not approved for institution')
    return Response(storage.read(report.path),media_type='application/pdf',headers={'Content-Disposition':f'attachment; filename="proofgraph-{report.kind}-{report_id}.pdf"'})
