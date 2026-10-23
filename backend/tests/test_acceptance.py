import fitz
from sqlalchemy import select, update
from app.audit import verify_audit
from app.models import AuditEvent,Rule,RuleVersion,Finding


def test_hero_lab_graph_and_highlight(client,auth):
    h=auth()
    r=client.get('/api/cases/1',headers=h)
    assert r.status_code==200
    case=r.json()
    contradiction=next(f for f in case['findings'] if f['title']=='Laboratories conflict' and f['manual_status']!='SUPERSEDED')
    assert {contradiction['source_a']['value'],contradiction['source_b']['value']}=={'18','15'}
    assert len(contradiction['source_a']['bbox'])==4
    assert contradiction['source_a']['page']==1
    assert contradiction['rule_id']=='SAMPLE-LAB-001'
    history=next(f for f in case['findings'] if f['title']=='Unexplained change: laboratories' and f['manual_status']!='SUPERSEDED')
    assert history['source_a']['value']=='18' and history['source_b']['value']=='12'
    assert all(k in contradiction for k in ['official_status','consistency_status','ai_status','manual_status'])
    assert contradiction['official_status']=='PENDING'
    graph=client.get('/api/cases/1/graph',headers=h).json()
    assert any(e['type']=='contradicts' for e in graph['edges'])
    assert any(n['type']=='Rule' for n in graph['nodes'])
    assert any(n['type']=='OfficialRecord' and 'NOT CONNECTED' in n['label'] for n in graph['nodes'])
    source=client.get(f"/api/documents/{contradiction['source_a']['document_id']}/file",headers=h)
    assert source.status_code==200 and source.content.startswith(b'%PDF')


def test_expired_duplicate_and_unavailable_source(client,auth):
    case=client.get('/api/cases/2',headers=auth()).json()
    active=[f for f in case['findings'] if f['manual_status']!='SUPERSEDED']
    assert any(f['title']=='Expired: Fire Safety Certificate' for f in active)
    assert any('Cross-institution similar document' in f['title'] for f in active)
    assert any(v['simulated'] and v['status']=='SOURCE_UNAVAILABLE' for v in case['verifications'])
    assert not any(v['status']=='VERIFIED_OFFICIAL' for v in case['verifications'])


def test_clean_case_not_overflagged(client,auth):
    data=client.get('/api/cases/3',headers=auth()).json()
    assert not [f for f in data['findings'] if f['manual_status']!='SUPERSEDED']
    assert data['priority']['label']=='Low'


def test_permissions_and_no_unofficial_verification(client,auth):
    institution=auth('institution')
    assert client.get('/api/cases/1',headers=institution).status_code==200
    assert client.get('/api/cases/2',headers=institution).status_code==403
    assert client.post('/api/findings/1/review',headers=institution,json={'action':'Confirm','reason':'Approved'}).status_code==403
    officer=auth('officer')
    r=client.post('/api/cases/1/verification/simulate?status=SOURCE_UNAVAILABLE',headers=officer)
    assert r.status_code==200 and r.json()['simulated'] and not r.json()['officially_verified']
    result=client.get('/api/cases/1',headers=officer).json()
    assert result['verifications'][-1]['status']=='SOURCE_UNAVAILABLE'


def test_review_audit_and_tamper_detection(client,auth):
    h=auth()
    findings=client.get('/api/cases/1',headers=h).json()['findings']
    f=next(f for f in findings if f['title']=='Laboratories conflict')
    r=client.post(f"/api/findings/{f['id']}/review",headers=h,json={'action':'Request evidence','reason':'Inventory report differs from application'})
    assert r.status_code==200
    audit=client.get('/api/audit/verify',headers=h).json()
    assert audit['valid']
    with client.test_factory() as session:
        event=session.scalars(select(AuditEvent).order_by(AuditEvent.id.desc())).first()
        event.action='FORGED_ENTRY'
        session.flush()
        assert not verify_audit(session)['valid']
        session.rollback()
    assert client.get('/api/audit/verify',headers=h).json()['valid']


def test_correction_refreshes_contradiction(client,auth):
    h=auth()
    case=client.get('/api/cases/1',headers=h).json()
    main=next(d for d in case['documents'] if d['kind']=='Application Form')
    field=next(f for f in main['fields'] if f['key']=='laboratories')
    r=client.patch(f"/api/fields/{field['id']}",headers=h,json={'value':'15','reason':'Validated against inventory'})
    assert r.status_code==200
    after=client.get('/api/cases/1',headers=h).json()
    assert not any(f['title']=='Laboratories conflict' and f['manual_status']!='SUPERSEDED' for f in after['findings'])
    assert any(f['title']=='Unexplained change: laboratories' and f['source_a']['value']=='15' and f['manual_status']!='SUPERSEDED' for f in after['findings'])
    assert any(a['action']=='CORRECT_EXTRACTED_FIELD' for a in client.get('/api/audit',headers=h).json())


def test_report_pdf_and_approval(client,auth):
    h=auth()
    report=client.post('/api/cases/1/reports?kind=deficiency',headers=h).json()
    assert report['draft'] and report['approval_required']
    raw=client.get(report['url'],headers=h)
    assert raw.status_code==200
    with fitz.open(stream=raw.content,filetype='pdf') as pdf:
        txt=' '.join(page.get_text() for page in pdf)
        assert 'SYNTHETIC DEMONSTRATION DATA' in txt
        assert 'Laboratories conflict' in txt
    assert client.post(f"/api/reports/{report['report_id']}/approve",headers=h).status_code==403
    assert client.post(f"/api/reports/{report['report_id']}/approve",headers=auth('senior')).json()['approved']


def test_rule_immutability_and_evaluation(client,auth):
    eval_result=client.get('/api/evaluation',headers=auth()).json()
    assert eval_result['cases']==30
    assert eval_result['dataset'].lower().find('synthetic')>=0
    admin=auth('admin')
    rule_data=client.get('/api/rules',headers=admin).json()['rules']
    original=next(x for x in rule_data if x['id']=='SAMPLE-LAB-001')
    new=client.post('/api/rules/SAMPLE-LAB-001/version',headers=admin,json={'severity':'Medium','specification':original['specification'],'source_citation':'SAMPLE test of immutable versions','effective_from':'2026-01-01'})
    assert new.status_code==200 and new.json()['version']==original['version']+1
    with client.test_factory() as session:
        rule=session.scalars(select(Rule).where(Rule.rule_id=='SAMPLE-LAB-001')).first()
        assert len(session.scalars(select(RuleVersion).where(RuleVersion.rule_id==rule.id)).all())>=2


def test_browser_cors_and_cross_tenant_evidence_mask(client,auth):
    r=client.options('/api/cases',headers={'Origin':'http://127.0.0.1:3000',
        'Access-Control-Request-Method':'GET','Access-Control-Request-Headers':'authorization'})
    assert r.status_code==200
    assert r.headers.get('access-control-allow-origin')=='http://127.0.0.1:3000'
    institution=auth('institution')
    case=client.get('/api/cases/1',headers=institution).json()
    for f in case['findings']:
        for k in ('source_a','source_b'):
            assert f[k].get('document_name','').startswith('Other institution') is False or f[k]['document_id'] is None
    graph=client.get('/api/cases/1/graph',headers=institution).json()
    assert not any(n['data'].get('external_to_case') for n in graph['nodes'])
    assert client.get('/api/cases/1/patterns',headers=institution).json()['patterns']==[]


def test_new_rule_version_is_cited_by_new_finding(client,auth):
    h=auth('admin')
    data=client.get('/api/rules',headers=h).json()['rules']
    rule=next(x for x in data if x['id']=='SAMPLE-LAB-001')
    r=client.post('/api/rules/SAMPLE-LAB-001/version',headers=h,json={
        'severity':'Medium','specification':rule['specification'],
        'source_citation':'SAMPLE revised laboratory check','effective_from':'2026-01-01'})
    assert r.status_code==200
    new_version=r.json()['version']
    assert client.post('/api/cases/1/revalidate',headers=h).status_code==200
    findings=client.get('/api/cases/1',headers=h).json()['findings']
    active=[f for f in findings if f['title']=='Laboratories conflict' and f['manual_status']!='SUPERSEDED']
    assert len(active)==1
    assert active[0]['rule_version']==new_version
    assert active[0]['severity']=='Medium'


def test_institution_preflight_upload_and_submit(client, auth):
    """A new portal case should actually process PDF bytes and show source-linked checks."""
    from seed import pdf
    login=auth('institution')
    institution_id=client.get('/api/institutions',headers=login).json()[0]['id']
    created=client.post('/api/cases',headers=login,json={'institution_id':institution_id,'category':'Extension of Approval','year':2026})
    assert created.status_code==200
    case_id=created.json()['id']
    for name,title,fields,kind in [
        ('application.pdf','Application Form',{'Laboratories':'18'},'Application Form'),
        ('rooms.pdf','Room Inventory',{'Laboratories':'15'},'Room Inventory'),
    ]:
        data=pdf(title,fields)
        uploaded=client.post(f'/api/cases/{case_id}/documents',headers=login,
            files={'file':(name,data,'application/pdf')},data={'kind':kind})
        assert uploaded.status_code==200,uploaded.text
        assert uploaded.json()['fields_found']>=1
    details=client.get(f'/api/cases/{case_id}',headers=login).json()
    active=[f for f in details['findings'] if f['manual_status']!='SUPERSEDED']
    disagreement=next(f for f in active if f['title']=='Laboratories conflict')
    assert disagreement['source_a']['document_id'] in {d['id'] for d in details['documents']}
    assert disagreement['source_b']['document_id'] in {d['id'] for d in details['documents']}
    assert [v['present'] for v in details['checklist']]==[True,True,False]
    submitted=client.post(f'/api/cases/{case_id}/submit',headers=login)
    assert submitted.status_code==200
    rejected=client.post(f'/api/cases/{case_id}/documents',headers=login,
        files={'file':('new.pdf',pdf('Room Inventory',{'Laboratories':'18'}),'application/pdf')})
    assert rejected.status_code==403
