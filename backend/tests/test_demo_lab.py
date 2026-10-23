"""Exercise actual validation and user-upload flow that the Interactive Demo presents."""
from pathlib import Path

SAMPLES = Path(__file__).resolve().parents[2] / 'frontend' / 'public' / 'samples'


def test_demo_run_reports_laboratory_disagreement_and_source_links(client, auth):
    h = auth('officer')
    run = client.post('/api/cases/1/revalidate', headers=h)
    assert run.status_code == 200, run.text
    case = client.get('/api/cases/1', headers=h).json()
    conflicts = [f for f in case['findings'] if f['consistency_status'] == 'CONTRADICTION' and f['manual_status'] != 'SUPERSEDED']
    assert any({f['source_a']['value'], f['source_b']['value']} == {'18', '15'} for f in conflicts)
    for finding in conflicts:
        assert finding['rule_id'] and finding['rule_version']
        assert finding['source_a'].get('page')
        assert finding['source_a'].get('bbox')
    assert any(c['key'] == 'laboratories' and c['old_value'] == '12' and c['new_value'] == '18' for c in case['changes'])
    graph = client.get('/api/cases/1/graph', headers=h).json()
    assert any(e['type'] == 'contradicts' for e in graph['edges'])


def test_demo_clean_control_has_no_high_severity(client, auth):
    h = auth('officer')
    assert client.post('/api/cases/3/revalidate', headers=h).status_code == 200
    case = client.get('/api/cases/3', headers=h).json()
    assert not [f for f in case['findings'] if f['severity'] == 'High' and f['manual_status'] != 'SUPERSEDED']


def test_sample_pdfs_trigger_and_resolve_real_document_contradiction(client, auth):
    h = auth('institution')
    institution = client.get('/api/institutions', headers=h).json()[0]
    created = client.post('/api/cases', headers=h, json={'institution_id': institution['id'], 'category': 'Extension of Approval', 'year': 2026})
    assert created.status_code == 200, created.text
    case_id = created.json()['id']
    for filename in ('Application_Form_18_Labs_DEMO.pdf', 'Room_Inventory_15_Labs_DEMO.pdf', 'Fire_Safety_Certificate_2028_DEMO.pdf'):
        data = (SAMPLES / filename).read_bytes()
        response = client.post(f'/api/cases/{case_id}/documents', headers=h, files={'file': (filename, data, 'application/pdf')})
        assert response.status_code == 200, response.text
        assert response.json()['fields_found'] >= 2
    case = client.get(f'/api/cases/{case_id}', headers=h).json()
    mismatch = [f for f in case['findings'] if f['consistency_status'] == 'CONTRADICTION' and f['manual_status'] != 'SUPERSEDED']
    assert any({f['source_a']['value'], f['source_b']['value']} == {'18', '15'} for f in mismatch)
    inventory = next(d for d in case['documents'] if d['kind'] == 'Room Inventory')
    field = next(f for f in inventory['fields'] if f['key'] == 'laboratories')
    fixed = client.patch(f'/api/fields/{field["id"]}', headers=h, json={'value': '18', 'reason': 'Correction to match recorded laboratory inventory'})
    assert fixed.status_code == 200, fixed.text
    updated = client.get(f'/api/cases/{case_id}', headers=h).json()
    assert not [f for f in updated['findings'] if f['consistency_status'] == 'CONTRADICTION' and f['manual_status'] != 'SUPERSEDED']
