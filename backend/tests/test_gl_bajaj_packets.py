"""Actual upload/extraction/validation regression using public training packets."""
from pathlib import Path
import pytest
from app.processing import process_bytes

ROOT=Path(__file__).resolve().parents[2]/'frontend'/'public'/'sample-packets'

@pytest.mark.parametrize('kind,expected_issues', [('consistent',0),('needs-review',2)])
def test_gl_bajaj_source_packets(client,auth,kind,expected_issues):
    headers=auth('officer')
    institutions=client.get('/api/institutions',headers=headers).json()
    institution=next(i for i in institutions if 'G L Bajaj' in i['name'])
    created=client.post('/api/cases',headers=headers,json={'institution_id':institution['id'],'category':'Extension of Approval','year':2026})
    assert created.status_code==200,created.text
    case_id=created.json()['id']
    for pdf in sorted((ROOT/kind).glob('*.pdf')):
        parsed=process_bytes(pdf.read_bytes(),pdf.name)
        assert 'institution_name' in [f['key'] for f in parsed['fields']]
        result=client.post(f'/api/cases/{case_id}/documents',headers=headers,files={'file':(pdf.name,pdf.read_bytes(),'application/pdf')})
        assert result.status_code==200,result.text
        assert result.json()['fields_found']>=2
    d=client.get(f'/api/cases/{case_id}',headers=headers).json()
    issues=[f for f in d['findings'] if f['manual_status']!='SUPERSEDED']
    assert len(issues)==expected_issues,[(f['title'],f['reason']) for f in issues]
    if kind=='needs-review':
        assert any({f['source_a']['value'],f['source_b']['value']}=={'18','15'} for f in issues if f['consistency_status']=='CONTRADICTION')
        assert any(f['consistency_status']=='EXPIRED' for f in issues)
    generated=client.post(f'/api/cases/{case_id}/reports?kind=evidence',headers=headers)
    assert generated.status_code==200,generated.text
    document=client.get(f"/api/reports/{generated.json()['report_id']}/file",headers=headers)
    assert document.status_code==200 and document.content.startswith(b'%PDF')
