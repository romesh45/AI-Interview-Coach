"""
Resume upload / delete tests.

Uses a minimal valid PDF (created in-memory) so no fixture file needed.
"""

import io


def _minimal_pdf() -> bytes:
    """Return the smallest valid text-extractable PDF."""
    return (
        b'%PDF-1.4\n'
        b'1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n'
        b'2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n'
        b'3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R'
        b'/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n'
        b'4 0 obj<</Length 44>>stream\nBT /F1 12 Tf 100 700 Td (Hello) Tj ET\nendstream\nendobj\n'
        b'5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n'
        b'xref\n0 6\n0000000000 65535 f \n'
        b'trailer<</Size 6/Root 1 0 R>>\nstartxref\n9\n%%EOF'
    )


def test_upload_non_pdf_rejected(auth_client):
    res = auth_client.post('/api/upload-resume', data={
        'resume_pdf': (io.BytesIO(b'not a pdf'), 'resume.txt'),
    }, content_type='multipart/form-data')
    assert res.status_code == 400
    data = res.get_json()
    assert 'error' in data
    assert 'PDF' in data['error']


def test_upload_no_file_rejected(auth_client):
    res = auth_client.post('/api/upload-resume', data={})
    assert res.status_code == 400
    assert 'error' in res.get_json()


def test_delete_when_no_resume(auth_client):
    # Clear any existing session resume first
    with auth_client.session_transaction() as sess:
        sess.pop('uploaded_resume_filename', None)

    res = auth_client.delete('/api/upload-resume')
    assert res.status_code == 404
    assert 'error' in res.get_json()


def test_history_page_loads(auth_client):
    res = auth_client.get('/history')
    assert res.status_code == 200
    assert b'Past Sessions' in res.data


def test_api_scores_no_session(auth_client):
    with auth_client.session_transaction() as sess:
        sess.pop('active_session_id', None)
    res = auth_client.get('/api/scores')
    assert res.status_code == 200
    data = res.get_json()
    assert data['scores'] == []
    assert data['average'] == 0
