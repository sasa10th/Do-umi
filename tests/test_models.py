import pytest
from datetime import date, timedelta
from app import create_app, db
from app.models import User, Penalty, Document, Exemption, PenaltyStandard


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


class TestUserModel:
    def test_password_hashing(self, app):
        with app.app_context():
            u = User(email='a@sasa.hs.kr', name='A')
            u.password = 'mypass'
            assert u.verify_password('mypass')
            assert not u.verify_password('wrong')

    def test_total_penalty_points(self, app):
        with app.app_context():
            u = User(email='b@sasa.hs.kr', name='B')
            u.password = 'pass'
            db.session.add(u)
            db.session.flush()
            p1 = Penalty(student_id=u.id, category='규정', reason='위반', points=3, date=date.today())
            p2 = Penalty(student_id=u.id, category='규정', reason='위반2', points=2, date=date.today())
            p3 = Penalty(student_id=u.id, category='상점', reason='모범', merit_points=1, date=date.today())
            db.session.add_all([p1, p2, p3])
            db.session.commit()
            assert u.total_penalty_points == 4  # 5 - 1

    def test_stage_calculation(self, app):
        with app.app_context():
            u = User(email='c@sasa.hs.kr', name='C')
            u.password = 'pass'
            db.session.add(u)
            db.session.flush()
            assert u.stage == 1
            p = Penalty(student_id=u.id, category='규정', reason='위반', points=7, date=date.today())
            db.session.add(p)
            db.session.commit()
            assert u.stage == 2

    def test_exemption_count(self, app):
        with app.app_context():
            u = User(email='d@sasa.hs.kr', name='D')
            u.password = 'pass'
            db.session.add(u)
            db.session.flush()
            e1 = Exemption(student_id=u.id)
            e2 = Exemption(student_id=u.id)
            db.session.add_all([e1, e2])
            db.session.commit()
            assert u.exemption_count == 2


class TestDocumentModel:
    def test_days_remaining(self, app):
        with app.app_context():
            u = User(email='e@sasa.hs.kr', name='E')
            u.password = 'p'
            db.session.add(u)
            db.session.flush()
            future = date.today() + timedelta(days=5)
            d = Document(student_id=u.id, title='Test', doc_type='천자문', due_date=future)
            db.session.add(d)
            db.session.commit()
            assert d.days_remaining == 5
            assert not d.is_overdue

    def test_overdue(self, app):
        with app.app_context():
            u = User(email='f@sasa.hs.kr', name='F')
            u.password = 'p'
            db.session.add(u)
            db.session.flush()
            past = date.today() - timedelta(days=3)
            d = Document(student_id=u.id, title='Past', doc_type='천자문', due_date=past)
            db.session.add(d)
            db.session.commit()
            assert d.is_overdue