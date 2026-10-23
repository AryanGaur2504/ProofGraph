"""Evidence-linked deterministic checks. Every check is a versioned SAMPLE demo rule."""
from collections import defaultdict
from datetime import date
from sqlalchemy import select, delete, text
from sqlalchemy.orm import Session
from .models import (Application, Institution, Document, ExtractedField, Claim, GraphNode, GraphEdge,
                     Finding, FindingEvidence, ChangeRecord, ApplicationSnapshot)
from .rules import checklist, current_rules


def ref(field, doc):
    if not field or not doc: return {'document_id':None,'document_name':'Not provided','field':None,'page':None,'bbox':[], 'value':None}
    return {'document_id':doc.id,'document_name':doc.name,'field_id':field.id,'field':field.key,'page':field.page,'bbox':field.bbox,'value':field.value}

def make_finding(db, app_id, rule, title, reason, action, a, b=None, category=None, consistency='NOT_CHECKED', ai='NOT_EVALUATED'):
    existing=db.scalars(select(Finding).where(Finding.application_id==app_id,Finding.rule_id==rule['id'],Finding.title==title,Finding.manual_status!='SUPERSEDED')).first()
    if existing:
        finding=existing
        old_pair=(finding.source_a,finding.source_b)
        if old_pair != (a,b or {}) or finding.rule_version != rule['version'] or finding.severity != rule['severity']:
            # Retain the reviewed record and its audit trail; create a fresh finding.
            finding.manual_status='SUPERSEDED'
            existing=None
    if not existing:
        finding=Finding(application_id=app_id,title=title,category=category or rule['category'],severity=rule['severity'],reason=reason,next_action=action,rule_id=rule['id'],rule_version=rule['version'],source_a=a or {},source_b=b or {},official_status='PENDING',consistency_status=consistency,ai_status=ai,manual_status='PENDING_REVIEW')
        db.add(finding); db.flush()
        for side, source in [('A',a),('B',b)]:
            if source and source.get('document_id'):
                db.add(FindingEvidence(finding_id=finding.id,document_id=source['document_id'],field_id=source.get('field_id'),page=source.get('page') or 1,bbox=source.get('bbox') or [],side=side))
    else:
        finding.reason=reason; finding.next_action=action; finding.consistency_status=consistency; finding.ai_status=ai
    return finding

def validate_case(db:Session, app_id:int):
    app=db.get(Application,app_id)
    if not app: raise ValueError('No application')
    docs=db.scalars(select(Document).where(Document.application_id==app_id)).all()
    fields={d.id:db.scalars(select(ExtractedField).where(ExtractedField.document_id==d.id)).all() for d in docs}
    rule_map={r['specification']['op']:r for r in current_rules(db)}
    produced=set()
    def add(rule, title, reason, action, a, b=None, consistency='NOT_CHECKED', ai='NOT_EVALUATED'):
        f=make_finding(db,app_id,rule,title,reason,action,a,b,consistency=consistency,ai=ai)
        produced.add(f.id)
    # Mandatory documents: absence cannot cite a nonexistent file; rule and checklist are provenance.
    for required in checklist(db,app.category):
        if not any(d.kind==required for d in docs):
            rule=rule_map['required_documents']
            add(rule,f'Missing: {required}',f'The sample checklist for {app.category} lists {required}; no matching uploaded file is present.','Request the missing document before completeness approval.',{'document_id':None,'document_name':'MISSING','field':required,'value':'NOT PROVIDED','page':None,'bbox':[]},consistency='INCOMPLETE')
    # Expiry checks are based on document-extracted date, not any regulatory threshold.
    for doc in docs:
        if doc.expiry:
            try: expired=date.fromisoformat(doc.expiry) < date.today()
            except ValueError: expired=False
            if expired:
                rule=rule_map['expired_documents']
                expiry_field=next((f for f in fields[doc.id] if f.key=='expiry'),None)
                add(rule,f'Expired: {doc.kind}',f'{doc.kind} shows expiry {doc.expiry} before the current date. This is a demo date check.','Request an updated certificate and manually verify with the issuing authority.',ref(expiry_field,doc) if expiry_field else {'document_id':doc.id,'document_name':doc.name,'field':'expiry','page':1,'bbox':[],'value':doc.expiry},consistency='EXPIRED')
    # Contradictions: compare like-for-like fields from different source documents.
    grouped=defaultdict(list)
    for doc in docs:
        for field in fields[doc.id]: grouped[field.key].append((field,doc))
    for key,entries in grouped.items():
        for i,(field_a,doc_a) in enumerate(entries):
            for field_b,doc_b in entries[i+1:]:
                if doc_a.id==doc_b.id or field_a.value.strip().casefold()==field_b.value.strip().casefold(): continue
                # Multiple field types supported. The sample rule is explicit for laboratories.
                if key!='laboratories' and (key not in rule_map['compare_other_fields']['specification'].get('fields',[])): continue
                rule=rule_map['compare_fields'] if key=='laboratories' else rule_map['compare_other_fields']
                add(rule,f'{key.replace("_"," ").title()} conflict',f'{doc_a.kind} says {field_a.value}; {doc_b.kind} says {field_b.value}. These are internally inconsistent claims, not proven misrepresentation.','Compare both source pages; request reconciled records or verify on inspection.',ref(field_a,doc_a),ref(field_b,doc_b),consistency='CONTRADICTION')
    # Arithmetic comparison of block-area evidence (no regulatory minimum asserted).
    totals=grouped.get('total_area',[])
    blocks_a=grouped.get('block_a_area',[])
    blocks_b=grouped.get('block_b_area',[])
    if totals and blocks_a and blocks_b and 'area_arithmetic' in rule_map:
        try:
            total=float(totals[0][0].value); calculated=float(blocks_a[0][0].value)+float(blocks_b[0][0].value)
            if abs(total-calculated)>0.00001:
                rule=rule_map['area_arithmetic']
                add(rule,'Area arithmetic does not reconcile',f'Total area {total} differs from block sum {calculated}. Units must be checked by the officer.',
                    'Request the area survey and calculation worksheet.',ref(totals[0][0],totals[0][1]),ref(blocks_a[0][0],blocks_a[0][1]),consistency='CONTRADICTION')
        except ValueError: pass
    # Historical diff is sourced from prior year's saved snapshot and current application form.
    prior=db.scalars(select(ApplicationSnapshot).where(ApplicationSnapshot.application_id==app_id).order_by(ApplicationSnapshot.year.desc())).first()
    current_doc=next((d for d in docs if d.kind=='Application Form'),None)
    current={f.key:f for f in fields.get(current_doc.id,[])} if current_doc else {}
    db.execute(delete(ChangeRecord).where(ChangeRecord.application_id==app_id))
    if prior:
        for key,old in prior.fields.items():
            if key not in current or str(old).strip()==current[key].value.strip(): continue
            explained=any(d.kind=='Expansion Evidence' for d in docs)
            rule=rule_map['historical_diff']
            change=ChangeRecord(application_id=app_id,key=key,old_value=str(old),new_value=current[key].value,explained=explained,explanation='Expansion evidence attached; needs human checking' if explained else 'No supporting change evidence identified',evidence_required=rule['specification']['evidence_required'])
            db.add(change)
            if not explained:
                add(rule,f'Unexplained change: {key.replace("_"," ")}',f'{prior.year} recorded {old}, while the current application declares {current[key].value}. Historical differences require context, not automatic adverse action.','Request the supporting change/expansion evidence and record officer determination.',ref(current[key],current_doc),{'document_id':None,'document_name':f'Historical snapshot {prior.year}','field':key,'value':str(old),'page':None,'bbox':[]},consistency='HISTORICAL_CHANGE')
    # Exact hashes, plus perceptual near-equality if dependencies are installed.
    for doc in docs:
        others=db.scalars(select(Document).where(Document.id!=doc.id)).all()
        for other in others:
            other_app=db.get(Application,other.application_id)
            if other_app.institution_id==app.institution_id: continue
            same_exact=bool(doc.sha256 and doc.sha256==other.sha256)
            similar=False
            if doc.mime.startswith('image/') and other.mime.startswith('image/') and doc.kind==other.kind and doc.perceptual_hash and other.perceptual_hash:
                try:
                    hd=(int(doc.perceptual_hash,16)^int(other.perceptual_hash,16)).bit_count()
                    similar=hd<=3
                except ValueError: pass
            if not (same_exact or similar): continue
            rule=rule_map['duplicate_cross_institution']
            add(rule,f'Cross-institution similar document: {doc.kind}',f'{doc.name} resembles {other.name} submitted by another institution ({"exact SHA-256" if same_exact else "perceptual image hash"}). This is a review signal, NOT proof of reuse or forgery.','Inspect both copies and seek authorized confirmation of document identity.',{'document_id':doc.id,'document_name':doc.name,'field':'sha256 / perceptual hash','value':doc.sha256[:14],'page':1,'bbox':[]},{'document_id':other.id,'document_name':other.name,'field':'sha256 / perceptual hash','value':other.sha256[:14],'page':1,'bbox':[]},ai='PRELIMINARY_PATTERN')
            break
    for old in db.scalars(select(Finding).where(Finding.application_id==app_id,Finding.manual_status!='SUPERSEDED')).all():
        if old.id not in produced: old.manual_status='SUPERSEDED'
    rebuild_graph(db,app_id)
    db.flush()
    return {'active_findings':len(produced),'documents':len(docs)}

def rebuild_graph(db:Session,app_id):
    db.execute(delete(GraphEdge).where(GraphEdge.application_id==app_id))
    db.execute(delete(GraphNode).where(GraphNode.application_id==app_id))
    db.flush()
    app=db.get(Application,app_id)
    institution=db.get(Institution,app.institution_id)
    nodes=[];edges=[]; node_ids={}
    def node(entity_type,entity_id,label,data=None):
        n=GraphNode(application_id=app_id,entity_type=entity_type,entity_id=entity_id,label=label,data=data or {})
        db.add(n);db.flush();nodes.append(n);node_ids[(entity_type,entity_id)]=n.id;return n.id
    def edge(a,b,kind,details=None):
        db.add(GraphEdge(application_id=app_id,source_id=a,target_id=b,relationship=kind,data=details or {}))
    root=node('Institution',institution.id,institution.name)
    appnode=node('Application',app.id,f'{app.category} · {app.year}')
    edge(root,appnode,'asserts')
    source=node('OfficialRecord',None,'NOT CONNECTED · verification pending',{'official_verification':'PENDING','simulated':False})
    edge(appnode,source,'governed_by',{'meaning':'No official record connected. Never infer authenticity.'})
    named_field_nodes={}
    for d in db.scalars(select(Document).where(Document.application_id==app_id)):
        dn=node('Document',d.id,d.kind,{'document_id':d.id,'filename':d.name})
        edge(appnode,dn,'evidenced_by')
        for f in db.scalars(select(ExtractedField).where(ExtractedField.document_id==d.id)):
            fn=node('ExtractedField',f.id,f'{f.key}: {f.value}',{'document_id':d.id,'page':f.page,'bbox':f.bbox,'field_id':f.id})
            edge(fn,dn,'extracted_from')
            claim_record=db.scalars(select(Claim).where(Claim.application_id==app_id,Claim.source_field_id==f.id)).first()
            if not claim_record:
                claim_record=Claim(application_id=app_id,key=f.key,value=f.value,source_field_id=f.id)
                db.add(claim_record);db.flush()
            else: claim_record.value=f.value
            cn=node('Claim',claim_record.id,f'{f.key} = {f.value}',{'document_id':d.id,'page':f.page,'bbox':f.bbox,'field_id':f.id})
            edge(appnode,cn,'asserts');edge(cn,fn,'evidenced_by')
            named_field_nodes.setdefault(f.key,[]).append(fn)
            if f.key in ('signatory','address'):
                kind='Person' if f.key=='signatory' else 'Address'
                name_node=node(kind,f.id,f.value)
                edge(dn,name_node,'signed_by' if kind=='Person' else 'located_at')
    for same_key,numbers in named_field_nodes.items():
        if len(numbers)>1:
            candidates=[]
            for fieldnode in numbers:
                fnode=db.get(GraphNode,fieldnode)
                candidates.append((fieldnode,fnode.label.split(': ',1)[-1].casefold().strip()))
            for i,(a,value) in enumerate(candidates):
                for b,bvalue in candidates[i+1:]:
                    if value==bvalue: edge(a,b,'matches',{'basis':'Exact normalized text agreement is NOT official authentication'})
    prior=db.scalars(select(ApplicationSnapshot).where(ApplicationSnapshot.application_id==app_id).order_by(ApplicationSnapshot.year.desc())).first()
    if prior:
        for key,old in prior.fields.items():
            current=db.scalars(select(ExtractedField).join(Document,ExtractedField.document_id==Document.id).where(Document.application_id==app_id,Document.kind=='Application Form',ExtractedField.key==key)).first()
            if current and current.value!=str(old):
                history=node('Claim',None,f'{key}: {old} ({prior.year} snapshot)',{'historical':True,'year':prior.year})
                current_claim=db.scalars(select(Claim).where(Claim.application_id==app_id,Claim.source_field_id==current.id)).first()
                if current_claim and ('Claim',current_claim.id) in node_ids: edge(node_ids[('Claim',current_claim.id)],history,'supersedes',{'explanation':'Change requiring evidence, not proof of violation'})
    for finding in db.scalars(select(Finding).where(Finding.application_id==app_id,Finding.manual_status!='SUPERSEDED')):
        fn=node('Finding',finding.id,finding.title,{'finding_id':finding.id,'severity':finding.severity})
        rule_node_id=node_ids.get(('Rule',hash(finding.rule_id)))
        if not rule_node_id:
            rule_node_id=node('Rule',hash(finding.rule_id),f'{finding.rule_id} v{finding.rule_version} · SAMPLE',{'rule_id':finding.rule_id,'version':finding.rule_version})
        edge(fn,rule_node_id,'governed_by')
        a=finding.source_a or {};b=finding.source_b or {}
        if a.get('field_id') and ('ExtractedField',a['field_id']) in node_ids:
            edge(fn,node_ids[('ExtractedField',a['field_id'])],'evidenced_by')
        if b.get('field_id') and ('ExtractedField',b['field_id']) in node_ids:
            edge(fn,node_ids[('ExtractedField',b['field_id'])],'evidenced_by')
        if b.get('document_id') and ('Document',b['document_id']) not in node_ids:
            external=node('Document',b['document_id'],f"Other institution: {b.get('document_name','source')}",{'document_id':b['document_id'],'external_to_case':True})
            edge(fn,external,'matches',{'basis':'Cross-institution pattern requiring review'})
        if finding.consistency_status=='CONTRADICTION' and a.get('field_id') and b.get('field_id'):
            edge(node_ids[('ExtractedField',a['field_id'])],node_ids[('ExtractedField',b['field_id'])],'contradicts')

def graph_json(db,app_id):
    nodes=db.scalars(select(GraphNode).where(GraphNode.application_id==app_id)).all()
    edges=db.scalars(select(GraphEdge).where(GraphEdge.application_id==app_id)).all()
    return {'nodes':[{'id':str(n.id),'type':n.entity_type,'label':n.label,'entity_id':n.entity_id,'data':n.data} for n in nodes], 'edges':[{'id':str(e.id),'source':str(e.source_id),'target':str(e.target_id),'type':e.relationship} for e in edges]}

def neighborhood(db, node_id:int):
    """Recursive CTE example: reachable subgraph up to depth 3 in one SQLite statement."""
    rows=db.execute(text('''WITH RECURSIVE reachable(id,depth) AS (
      SELECT :node,0 UNION SELECT e.target_id,r.depth+1 FROM graph_edges e JOIN reachable r ON e.source_id=r.id WHERE r.depth<3
    ) SELECT DISTINCT id FROM reachable'''),{'node':node_id}).all()
    return [row[0] for row in rows]

def priority(findings):
    reasons=[{'finding_id':f.id,'severity':f.severity,'weight': {'High':5,'Medium':3,'Low':1}.get(f.severity,1),'title':f.title} for f in findings if f.manual_status!='SUPERSEDED']
    total=sum(r['weight'] for r in reasons)
    return {'label':'High' if total>=5 else ('Medium' if total>=3 else 'Low'), 'points':total,'formula':'SUM(High × 5 + Medium × 3 + Low × 1), sample queue prioritization only, not a fraud score','reasons':reasons}


def cross_institution_patterns(db:Session,app_id:int):
    application=db.get(Application,app_id)
    if application is None:return []
    docs=db.scalars(select(Document).where(Document.application_id==app_id)).all()
    otherdocs=db.scalars(select(Document).where(Document.application_id!=app_id)).all()
    out=[]; seen=set()
    for doc in docs:
        our_fields=db.scalars(select(ExtractedField).where(ExtractedField.document_id==doc.id)).all()
        for other in otherdocs:
            related=db.get(Application,other.application_id)
            if related.institution_id==application.institution_id:continue
            match=None
            if doc.sha256==other.sha256:match=('SHA-256 exact duplicate',doc.sha256[:18])
            if not match:
                their_fields=db.scalars(select(ExtractedField).where(ExtractedField.document_id==other.id)).all()
                for f in our_fields:
                    if f.key not in {'signatory','address','inspector_name','registration_id'}:continue
                    for g in their_fields:
                        if f.key==g.key and f.value.strip() and f.value.strip().casefold()==g.value.strip().casefold():
                            match=(f.key,f.value[:100]);break
                    if match:break
            if match and (doc.id,other.id) not in seen:
                seen.add((doc.id,other.id))
                out.append({'signal':match[0], 'shared_value':match[1], 'source_document_id':doc.id,'other_document_id':other.id,'other_institution':db.get(Institution,related.institution_id).name,'other_case_id':related.id,'assessment':'PATTERN NEEDING HUMAN REVIEW - NOT AN AUTHENTICITY FINDING'})
    return out
