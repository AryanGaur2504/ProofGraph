"""PDF reports should explain real discrepancies, not list every backend result."""
from pathlib import Path
import fitz
import pytest

PACKETS = Path(__file__).resolve().parents[2]/'frontend'/'public'/'sample-packets'


def report_text(client, headers, case_id):
    created = client.post(f'/api/cases/{case_id}/reports?kind=evidence', headers=headers)
    assert created.status_code == 200, created.text
    response = client.get(created.json()['url'], headers=headers)
    assert response.status_code == 200
    with fitz.open(stream=response.content, filetype='pdf') as pdf:
        return len(pdf), '\n'.join(page.get_text() for page in pdf)


@pytest.mark.parametrize('packet,expected_count', [('consistent', 0), ('needs-review', 2)])
def test_short_report_for_uploaded_gl_bajaj_packets(client, auth, packet, expected_count):
    h = auth()
    institutions = client.get('/api/institutions', headers=h).json()
    institution = next(i for i in institutions if 'G L Bajaj' in i['name'])
    case = client.post('/api/cases', headers=h, json={
        'institution_id': institution['id'], 'category': 'Extension of Approval', 'year': 2026,
    }).json()
    for path in sorted((PACKETS/packet).glob('*.pdf')):
        up = client.post(f"/api/cases/{case['id']}/documents", headers=h,
                         files={'file': (path.name, path.read_bytes(), 'application/pdf')})
        assert up.status_code == 200, up.text

    count, txt = report_text(client, h, case['id'])
    assert count == 1, f'Expected a concise 1-page report, got {count}'
    assert 'G L Bajaj' in txt
    assert '3 documents checked' in txt
    assert 'SYNTHETIC DEMONSTRATION DATA' in txt
    assert 'Documents reviewed' not in txt
    assert 'VERIFICATION AND DECISION STATUS' not in txt
    assert 'Not officially verified' not in txt  # compact, precise limitation instead
    assert 'Document comparison' in txt
    if expected_count == 0:
        assert 'No issues found in the checked fields' in txt
        assert 'What needs attention' not in txt
        assert 'Laboratory counts do not match' not in txt
    else:
        assert '2 items need attention' in txt
        assert 'What needs attention' in txt
        assert 'Laboratory counts do not match' in txt
        assert '18' in txt and '15' in txt
        assert 'Document has expired' in txt
        assert 'Compared documents' in txt
        assert 'Next step:' in txt


def test_resolved_or_dismissed_result_not_repeated_in_summary(client, auth):
    h = auth()
    case = client.get('/api/cases/1', headers=h).json()
    finding = next(x for x in case['findings'] if x['title'] == 'Laboratories conflict' and x['manual_status'] != 'SUPERSEDED')
    r = client.post(f"/api/findings/{finding['id']}/review", headers=h,
                    json={'action':'Dismiss', 'reason':'Officer found source was mislabeled'})
    assert r.status_code == 200
    _, txt = report_text(client, h, 1)
    assert 'Laboratory counts do not match' not in txt
    # Historical discrepancies may still be open and must not be hidden.
    assert 'A value changed since the previous application' in txt
