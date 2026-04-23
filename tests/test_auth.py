"""Auth route tests — register, login, logout, duplicate email."""


def test_register_success(client, db):
    res = client.post('/auth/register', data={
        'email': 'new@example.com',
        'password': 'securepass',
        'confirm_password': 'securepass',
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'InterviewAI' in res.data


def test_register_duplicate_email(client, db, app):
    with app.app_context():
        from models import User
        u = User(email='dupe@example.com')
        u.set_password('password123')
        db.session.add(u)
        db.session.commit()

    res = client.post('/auth/register', data={
        'email': 'dupe@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
    })
    assert b'already exists' in res.data


def test_register_password_too_short(client, db):
    res = client.post('/auth/register', data={
        'email': 'short@example.com',
        'password': 'abc',
        'confirm_password': 'abc',
    })
    assert b'8 characters' in res.data


def test_register_password_mismatch(client, db):
    res = client.post('/auth/register', data={
        'email': 'mismatch@example.com',
        'password': 'password123',
        'confirm_password': 'different123',
    })
    assert b'do not match' in res.data


def test_login_success(client, db, app):
    with app.app_context():
        from models import User
        u = User(email='login@example.com')
        u.set_password('mypassword')
        db.session.add(u)
        db.session.commit()

    res = client.post('/auth/login', data={
        'email': 'login@example.com',
        'password': 'mypassword',
    }, follow_redirects=True)
    assert res.status_code == 200


def test_login_wrong_password(client, db, app):
    with app.app_context():
        from models import User
        u = User(email='wrongpw@example.com')
        u.set_password('correctpassword')
        db.session.add(u)
        db.session.commit()

    res = client.post('/auth/login', data={
        'email': 'wrongpw@example.com',
        'password': 'wrongpassword',
    })
    assert b'Invalid email or password' in res.data


def test_logout(auth_client):
    res = auth_client.get('/auth/logout', follow_redirects=True)
    assert res.status_code == 200
    # After logout, accessing /app redirects to login
    res2 = auth_client.get('/app', follow_redirects=False)
    assert res2.status_code == 302


def test_protected_route_redirects_unauthenticated(client):
    res = client.get('/app', follow_redirects=False)
    assert res.status_code == 302
    assert '/auth/login' in res.headers['Location']
