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
    # 카테고리, 사유, 벌점, 상점
    standards_data = [
        ('생활규정', '아침 점호 지각오전 시까지 미등교저녁 점호 불참', 1, 0),
        ('생활규정', '호실 청결 상태 불량', 1, 0),
        ('생활규정', '학습 시간 지각무단 이석', 1, 0),
        ('생활규정', '귀사 시간 미 준수 및 귀가 신고 불이행', 2, 0),
        ('생활규정', '소란 행위취침 방해특별한 사유 없이 취침 시간에 호실 밖에 있는 경우', 2, 0),
        ('생활규정', '기숙사 내 허용되지 않은 음식물 및 물품 반입', 2, 0),
        ('생활규정', '휴게실 이외의 장소에서 취식시간 미준수', 2, 0),
        ('생활규정', '사전 신고 없이 자습 시간 중 호실 취침', 2, 0),
        ('생활규정', '타 호실 무단 출입 및 타 호실 취침', 3, 0),
        ('생활규정', '학습 공간에서 학습과 관계없는 행위게임드라마 시청 등를 하는 경우', 3, 0),
        ('생활규정', '기숙사 무단 출입 및 방조 (이용 가능 시각이 아님에도 출입하는 경우, 이용가능 대상이 아닌 학생이 기숙사에 머무를 수 있도록 조력하는 경우 등)', 3, 0),
        ('생활규정', '사감의 정당한 지시 불이행 (비명시 항목)', 5, 0),
        ('생활규정', '기숙사 사감의 승인 없이 배달음식을 기숙사에 반입 및 섭취', 5, 0),
        ('생활규정', '무단 외출 (기숙사동에서 이탈)', 5, 0),
        ('생활규정', '상기 내용에 포함되지 않았으나 뚜렷이 지도할 내용 (단, 생활교육위원회 회부 사안의 경우에는 벌점 5점 부여)', 1-5, 0),
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