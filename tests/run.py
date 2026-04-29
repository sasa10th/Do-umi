import os
from app import create_app, db
from app.models import User, Penalty, Document, Exemption, PenaltyStandard
from datetime import date, timedelta

app = create_app(os.environ.get('FLASK_ENV', 'development'))


def seed_db():
    """개발용 시드 데이터 생성"""
    if User.query.first():
        return  # 이미 데이터 있으면 스킵

    # 관리자 계정
    admin = User(
        email='admin@sasa.hs.kr',
        name='관리자',
        student_id='00000000',
        room_number='관리실',
        is_admin=True
    )
    admin.password = 'admin1234'
    db.session.add(admin)

    # 테스트 학생 계정
    student = User(
        email='20231001@sasa.hs.kr',
        name='김민기',
        student_id='20231001',
        room_number='302호',
        phone='010-1234-5678',
        grade=1
    )
    student.password = 'student1234'
    db.session.add(student)

    db.session.flush()  # ID 생성

    # 벌점 기준표
    standards_data = [
        ('생활규정', '취침시간 위반', 1, 0),
        ('생활규정', '복도 소음 유발', 1, 0),
        ('생활규정', '청소 불이행', 2, 0),
        ('학업규정', '수업 중 휴대폰 사용', 2, 0),
        ('학업규정', '자습 미참여', 1, 0),
        ('생활불량', '욕설 및 폭언', 3, 0),
        ('봉사활동', '기숙사 자율 봉사', 0, 2),
        ('우수행동', '모범 생활 인정', 0, 3),
    ]
    for cat, desc, pts, merit in standards_data:
        s = PenaltyStandard(category=cat, description=desc, penalty_points=pts, merit_points=merit)
        db.session.add(s)

    # 테스트 벌점 데이터
    penalties = [
        Penalty(student_id=student.id, issued_by_id=admin.id,
                date=date.today() - timedelta(days=10),
                category='생활규정', reason='복도 소음 유발', points=1),
        Penalty(student_id=student.id, issued_by_id=admin.id,
                date=date.today() - timedelta(days=5),
                category='학업규정', reason='수업 중 휴대폰 사용', points=2),
        Penalty(student_id=student.id, issued_by_id=admin.id,
                date=date.today() - timedelta(days=3),
                category='봉사활동', reason='모범 생활', merit_points=2),
    ]
    for p in penalties:
        db.session.add(p)

    # 테스트 천자문 문서
    docs = [
        Document(student_id=student.id, title='천자문 1-50자',
                 doc_type='천자문', due_date=date.today() + timedelta(days=7)),
        Document(student_id=student.id, title='천자문 51-100자',
                 doc_type='천자문', due_date=date.today() + timedelta(days=21)),
    ]
    for d in docs:
        db.session.add(d)

    # 면제권 1개 부여
    ex = Exemption(student_id=student.id, granted_by_id=admin.id, note='초기 지급')
    db.session.add(ex)

    db.session.commit()
    print('✅ 시드 데이터 생성 완료')
    print('📌 관리자: admin@sasa.hs.kr / admin1234')
    print('📌 학생:   20231001@sasa.hs.kr / student1234')


@app.cli.command('seed')
def seed_command():
    """DB 시드 데이터 생성: flask seed"""
    with app.app_context():
        db.create_all()
        seed_db()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_db()
    app.run(debug=True, host='0.0.0.0', port=5000)