"""Real offline processing, with optional and honestly bounded OCR/anomaly checks."""
import hashlib, io, re
from datetime import date
from PIL import Image, ImageChops
import fitz
from .storage import storage

KEYS = {'laboratories':'laboratories','lab count':'laboratories','faculty':'faculty_count', 'faculty count':'faculty_count', 'land area':'land_area', 'intake':'intake','institution name':'institution_name','certificate number':'certificate_number','expiry date':'expiry','address':'address','signatory':'signatory','registration id':'registration_id','latitude':'latitude','longitude':'longitude','total area':'total_area','block a area':'block_a_area','block b area':'block_b_area','building area':'building_area','inspector name':'inspector_name'}

def classify(text, name):
    lower=(text+' '+name).lower()
    if 'room inventory' in lower or 'room list' in lower: return 'Room Inventory'
    if 'fire safety' in lower: return 'Fire Safety Certificate'
    if 'building certificate' in lower: return 'Building Certificate'
    if 'name change evidence' in lower: return 'Name Change Evidence'
    if 'capacity evidence' in lower: return 'Capacity Evidence'
    if 'expansion evidence' in lower: return 'Expansion Evidence'
    if 'application form' in lower or 'declared laboratories' in lower: return 'Application Form'
    return 'Other'

def phash_image(image):
    try:
        import imagehash
        return str(imagehash.phash(image.convert('RGB')))
    except ImportError:
        return None

def _ocr_lines(image):
    try:
        import pytesseract
        # Hindi availability depends on locally installed Tesseract language packs.
        langs=pytesseract.get_languages(config='')
        language = 'eng+hin' if 'hin' in langs else 'eng'
        data=pytesseract.image_to_data(image,lang=language,output_type=pytesseract.Output.DICT)
        groups={}
        for i,word in enumerate(data['text']):
            if not word.strip(): continue
            key=(data['block_num'][i],data['par_num'][i],data['line_num'][i])
            left,top,width,height=(data[k][i] for k in ('left','top','width','height'))
            entry=groups.setdefault(key, {'words':[],'rects':[],'conf':[]})
            entry['words'].append(word)
            entry['rects'].append([left,top,left+width,top+height])
            try: entry['conf'].append(max(0, min(1, float(data['conf'][i])/100)))
            except (TypeError,ValueError): pass
        lines=[]
        for e in groups.values():
            r=e['rects']; lines.append((' '.join(e['words']), [min(z[0] for z in r),min(z[1] for z in r),max(z[2] for z in r),max(z[3] for z in r)],sum(e['conf'])/len(e['conf']) if e['conf'] else .5))
        return lines
    except Exception:
        return []

def process_bytes(raw:bytes, filename:str):
    digest=hashlib.sha256(raw).hexdigest()
    lines=[]; meta={}; image=None
    if filename.lower().endswith('.pdf'):
        with fitz.open(stream=raw,filetype='pdf') as doc:
            meta={'pdf_metadata': {k:(v or '')[:160] for k,v in doc.metadata.items()},'pages':len(doc),'signature_status':'UNDETERMINED: offline PDF signature trust-chain validation not configured'}
            for pi,page in enumerate(doc):
                page_lines=[]
                for block in page.get_text('dict')['blocks']:
                    for line in block.get('lines',[]):
                        spans=line.get('spans',[])
                        if not spans: continue
                        content=''.join(s['text'] for s in spans)
                        box=[min(s['bbox'][0] for s in spans),min(s['bbox'][1] for s in spans),max(s['bbox'][2] for s in spans),max(s['bbox'][3] for s in spans)]
                        page_lines.append((pi+1,content,box,0.99))
                if not page_lines:
                    pix=page.get_pixmap(matrix=fitz.Matrix(2,2))
                    img=Image.open(io.BytesIO(pix.tobytes('png')))
                    page_lines=[(pi+1,t,[v/2 for v in box],confidence) for t,box,confidence in _ocr_lines(img)]
                lines.extend(page_lines)
            if len(doc):
                image=Image.open(io.BytesIO(doc[0].get_pixmap(matrix=fitz.Matrix(0.7,0.7)).tobytes('png'))).convert('RGB')
    else:
        image=Image.open(io.BytesIO(raw)).convert('RGB')
        meta['image_dimensions']=list(image.size)
        meta['exif_present']=bool(image.getexif())
        lines=[(1,t,box,c) for t,box,c in _ocr_lines(image)]
        try:
            import cv2, numpy as np
            gray=cv2.cvtColor(np.array(image),cv2.COLOR_RGB2GRAY)
            result,_,_=cv2.QRCodeDetector().detectAndDecode(gray)
            if result: meta['qr_payload']=result[:200]
        except Exception: pass
    fields=[]
    for page,content,box,confidence in lines:
        match=re.match(r'\s*([^:]{2,50})\s*:\s*(.*?)\s*$',content)
        if not match: continue
        name=re.sub(r'\s+',' ',match.group(1).lower().strip())
        if name.startswith('declared '): name=name[9:]
        if name.startswith('inventory '): name=name[10:]
        key=KEYS.get(name)
        if key and match.group(2):
            fields.append({'key':key,'value':match.group(2),'page':page,'bbox':box,'confidence':round(confidence,2)})
    text='\n'.join(l[1] for l in lines)
    if image is not None:
        meta['perceptual_hash_method']='imagehash.phash first page/whole image, when library available'
    return {'sha256':digest,'perceptual_hash':phash_image(image) if image is not None else None,'metadata':meta,'kind':classify(text,filename),'fields':fields}

def advisory_signals(doc, raw):
    signals=[]
    meta=doc.metadata_json or {}
    pdfmeta=meta.get('pdf_metadata',{})
    if pdfmeta.get('modDate') and pdfmeta.get('creationDate') and pdfmeta['modDate']!=pdfmeta['creationDate']:
        signals.append({'signal':'PDF metadata dates differ','strength':'LOW','reason':'Creation and modification timestamp fields differ','limitations':'Normal editing and export can explain this; timestamps are user-editable'})
    if pdfmeta.get('producer'):
        signals.append({'signal':'PDF producer metadata','strength':'INFORMATIONAL','reason':f"Producer: {pdfmeta['producer'][:70]}",'limitations':'Metadata alone cannot authenticate a document'})
    if doc.mime.startswith('image/'):
        signals.append({'signal':'Infrastructure photo metadata','strength':'INFORMATIONAL','reason':'EXIF metadata is present' if meta.get('exif_present') else 'No EXIF metadata available','limitations':'EXIF can be removed or manipulated; absence is not evidence of fraud'})
        try:
            image=Image.open(io.BytesIO(raw)).convert('RGB')
            buff=io.BytesIO(); image.save(buff,format='JPEG',quality=90)
            recompressed=Image.open(io.BytesIO(buff.getvalue())).convert('RGB')
            bbox=ImageChops.difference(image,recompressed).getbbox()
            signals.append({'signal':'Recompression difference (ELA-style diagnostic)','strength':'INFORMATIONAL','reason': 'Image has nonzero recompression differences' if bbox else 'No difference detected at this setting','limitations':'Not a validated forgery classifier; do not interpret as proof of tampering'})
        except Exception: pass
    signals.append({'signal':'PDF signature / issuing authority','strength':'UNVERIFIED','reason':meta.get('signature_status','Not cryptographically authenticated'),'limitations':'An authorized trust chain and issuing-authority verification is required'})
    return signals
