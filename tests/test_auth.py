import pytest
from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def create_user(db_session, email='test@sasa.hs.kr', name='테스터', password='testpass1'):
    user = User(email=email, name=name)
    user.password = password
    db_session.add(user)
    db_session.commit()
    return user


class TestLogin:
    def test_login_page_loads(self, client):
        res = client.get('/auth/login')
        assert res.status_code == 200

    def test_login_success(self, client, app):
        with app.app_context():
            create_user(db)
        res = client.post('/auth/login', data={
            'email': 'test@sasa.hs.kr',
            'password': 'testpass1'
        }, follow_redirects=True)
        assert res.status_code == 200

    def test_login_wrong_password(self, client, app):
        with app.app_context():
            create_user(db)
        res = client.post('/auth/login', data={
            'email': 'test@sasa.hs.kr',
            'password': 'wrongpass'
        })
        assert '올바르지 않습니다' in res.data.decode('utf-8')

    def test_login_unknown_email(self, client):
        res = client.post('/auth/login', data={
            'email': 'unknown@sasa.hs.kr',
            'password': 'anypass'
        })
        assert '올바르지 않습니다' in res.data.decode('utf-8')


class TestSignup:
    def test_signup_page_loads(self, client):
        res = client.get('/auth/signup')
        assert res.status_code == 200

    def test_signup_success(self, client, app):
        res = client.post('/auth/signup', data={
            'email': 'new@sasa.hs.kr',
            'name': '신규학생',
            'password': 'newpass12',
            'password2': 'newpass12',
        }, follow_redirects=True)
        assert res.status_code == 200
        with app.app_context():
            assert User.query.filter_by(email='new@sasa.hs.kr').first() is not None

    def test_signup_invalid_domain(self, client):
        res = client.post('/auth/signup', data={
            'email': 'user@gmail.com',
            'name': '외부인',
            'password': 'pass1234',
            'password2': 'pass1234',
        })
        assert 'sasa.hs.kr' in res.data.decode('utf-8')

    def test_signup_password_mismatch(self, client):
        res = client.post('/auth/signup', data={
            'email': 'x@sasa.hs.kr',
            'name': '테스트',
            'password': 'pass1234',
            'password2': 'different',
        })
        assert '일치하지 않습니다' in res.data.decode('utf-8')

    def test_signup_duplicate_email(self, client, app):
        with app.app_context():
            create_user(db)
        res = client.post('/auth/signup', data={
            'email': 'test@sasa.hs.kr',
            'name': '중복',
            'password': 'pass1234',
            'password2': 'pass1234',
        })
        assert '이미 사용 중' in res.data.decode('utf-8')


class TestLogout:
    def test_logout_redirects(self, client, app):
        with app.app_context():
            create_user(db)
        client.post('/auth/login', data={'email': 'test@sasa.hs.kr', 'password': 'testpass1'})
        res = client.get('/auth/logout', follow_redirects=True)
        assert res.status_code == 200