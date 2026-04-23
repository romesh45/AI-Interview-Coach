"""
Interview flow tests — all run in demo mode (no OpenAI key needed).

Verifies: question generation, answer evaluation, reset, and
that demo mode returns realistic mock data.
"""


def test_interview_page_loads(auth_client):
    res = auth_client.get('/app')
    assert res.status_code == 200
    assert b'Set up your interview' in res.data


def test_demo_mode_banner_visible(auth_client):
    res = auth_client.get('/app')
    assert b'Demo Mode' in res.data


def test_generate_questions_demo(auth_client):
    res = auth_client.post('/app', data={
        'action': 'generate',
        'resume': 'Senior Python developer with 5 years Flask experience.',
        'job_description': 'Backend Engineer at a fintech startup.',
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Technical Questions' in res.data
    assert b'Behavioural Questions' in res.data


def test_generate_missing_resume(auth_client):
    res = auth_client.post('/app', data={
        'action': 'generate',
        'resume': '',
        'job_description': 'Backend Engineer role.',
    })
    assert res.status_code == 200
    assert b'Please provide both' in res.data or b'cannot be empty' in res.data


def test_generate_missing_jd(auth_client):
    res = auth_client.post('/app', data={
        'action': 'generate',
        'resume': 'Python developer with Flask experience.',
        'job_description': '',
    })
    assert res.status_code == 200
    assert b'Please provide both' in res.data or b'cannot be empty' in res.data


def test_evaluate_answer_demo(auth_client, app):
    # First generate a session
    auth_client.post('/app', data={
        'action': 'generate',
        'resume': 'Python developer, 3 years experience.',
        'job_description': 'Software Engineer — Python, Flask, REST APIs.',
    }, follow_redirects=True)

    # Get a question from demo data to evaluate against
    from demo_data import DEMO_QUESTIONS
    question = DEMO_QUESTIONS['technical'][0]['question']
    skill    = DEMO_QUESTIONS['technical'][0]['skill']

    res = auth_client.post('/app', data={
        'action': 'evaluate',
        'question': question,
        'answer': 'I would use cursor-based pagination for large datasets because it handles inserts and deletes consistently.',
        'skill': skill,
        'difficulty': 'hard',
        'q_type': 'technical',
    }, follow_redirects=True)
    assert res.status_code == 200
    # Score ring and feedback should appear
    assert b'score-ring' in res.data or b'eval-result' in res.data


def test_evaluate_empty_answer(auth_client, app):
    auth_client.post('/app', data={
        'action': 'generate',
        'resume': 'Python developer.',
        'job_description': 'Engineer role.',
    }, follow_redirects=True)

    from demo_data import DEMO_QUESTIONS
    question = DEMO_QUESTIONS['technical'][0]['question']

    res = auth_client.post('/app', data={
        'action': 'evaluate',
        'question': question,
        'answer': '',
        'skill': 'Python',
        'difficulty': 'medium',
        'q_type': 'technical',
    })
    assert b'Please write an answer' in res.data


def test_reset_clears_session(auth_client):
    auth_client.post('/app', data={
        'action': 'generate',
        'resume': 'Developer.',
        'job_description': 'Engineer role.',
    }, follow_redirects=True)

    res = auth_client.post('/app', data={'action': 'reset'}, follow_redirects=True)
    assert res.status_code == 200
    assert b'Set up your interview' in res.data


def test_dashboard_loads(auth_client):
    res = auth_client.get('/dashboard')
    assert res.status_code == 200
    assert b'Dashboard' in res.data


def test_profile_page_loads(auth_client):
    res = auth_client.get('/profile')
    assert res.status_code == 200
    assert b'Your Profile' in res.data
    assert b'test@example.com' in res.data
