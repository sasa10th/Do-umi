import os
from app import create_app, db
from app.models import User, Penalty, Document, Exemption, PenaltyStandard
from datetime import date, timedelta

app = create_app(os.environ.get('FLASK_ENV', 'development'))


def seed_db():
    """개발용 시드 데이터 생성"""

    # 관리자 계정
    admin = User.query.filter_by(email='admin@sasa.hs.kr').first()

    if not admin:
        admin = User(
            email='admin@sasa.hs.kr',
            name='관리자',
            student_id='99999',
            room_number='사감실',
            is_admin=True
        )
        admin.password = 'admin1234'
        db.session.add(admin)

    # 테스트 학생 계정
    student = User.query.filter_by(student_id='00000').first()

    if not student:
        student = User(
            email='guest@sasa.hs.kr',
            name='사용자',
            student_id='00000',
            room_number='000',
            phone='01012345678',
            grade=0
        )
        student.password = 'guest1234'
        db.session.add(student)

    db.session.flush()  # ID 생성

    # 기존 벌점 기준표 삭제
    db.session.query(PenaltyStandard).delete()

    # 벌점 기준표
    standards_data = [
        ('아침 점호 지각(오전 8시까지 미등교), 저녁 점호 불참', 1, 0),
        ('호실 청결 상태 불량', 1, 0),
        ('학습 시간 지각, 무단 이석', 1, 0),
        ('귀사 시간 미준수 및 귀가 신고 불이행', 2, 0),
        ('소란 행위, 취침 방해, 특별한 사유 없이 취침 시간에 호실 밖에 있는 경우', 2, 0),
        ('기숙사 내 허용되지 않은 음식물 및 물품 반입', 2, 0),
        ('휴게실 이외의 장소에서 취식, 시간 미준수', 2, 0),
        ('사전 신고 없이 자습 시간 중 호실 취침', 2, 0),
        ('타 호실 무단 출입 및 타 호실 취침', 3, 0),
        ('학습 공간에서 학습과 관계없는 행위(게임, 드라마 시청 등)를 하는 경우', 3, 0),
        ('기숙사 무단 출입 및 방조', 3, 0),
        ('사감의 정당한 지시 불이행 (비명시 항목)', 5, 0),
        ('기숙사 사감의 승인 없이 배달음식을 기숙사에 반입 및 섭취', 5, 0),
        ('무단 외출 (기숙사동에서 이탈)', 5, 0),
        ('상기 내용에 포함되지 않았으나 뚜렷이 지도할 내용', 5, 0),
        ('정당한 사유 없이 귀사하지 않음(무단 외박 포함)', 8, 0),
        ('사감에 대한 불손한 언행 및 태도', 10, 0),
        ('음주, 흡연, 절도 등 중요 위반 사항 확인시 영구 명령퇴사', 0, 0),

        ('기숙사 봉사활동 시간 참여', 0, 1),
        ('기숙사 내 분실물을 찾아주었을 때', 0, 1),
        ('기숙사 방 청결 상태 우수', 0, 1),
        ('몸이 불편한 학생의 기숙사 생활에 도움을 주었을 때', 0, 2),
        ('월간 기숙사 생활태도 우수 학생으로 선정된 경우', 0, 2),
        ('상기 내용에 포함되지 않았으나 뚜렷이 칭찬할 내용', 0, 2),
    ]

    for desc, pts, merit in standards_data:
        s = PenaltyStandard(
            description=desc,
            penalty_points=pts,
            merit_points=merit
        )
        db.session.add(s)

    # 테스트 벌점 데이터 없을 때만 추가
    if not Penalty.query.first():
        penalties = [
            Penalty(
                student_id=student.id,
                issued_by_id=admin.id,
                date=date.today() - timedelta(days=10),
                reason='소란 행위',
                points=2
            ),
            Penalty(
                student_id=student.id,
                issued_by_id=admin.id,
                date=date.today() - timedelta(days=5),
                reason='학습 시간 지각',
                points=1
            ),
            Penalty(
                student_id=student.id,
                issued_by_id=admin.id,
                date=date.today() - timedelta(days=3),
                reason='기숙사 봉사활동 시간 참여',
                merit_points=1
            ),
        ]

        for p in penalties:
            db.session.add(p)

    # 테스트 문서 없을 때만 추가
    if not Document.query.first():
        docs = [
            Document(
                student_id=student.id,
                doc_type='천자문',
                due_date=date.today() + timedelta(days=7)
            ),
            Document(
                student_id=student.id,
                doc_type='천자문',
                due_date=date.today() + timedelta(days=21)
            ),
        ]

        for d in docs:
            db.session.add(d)

    # 면제권 없을 때만 추가
    if not Exemption.query.first():
        ex = Exemption(
            student_id=student.id,
            granted_by_id=admin.id,
            note='초기 지급'
        )
        db.session.add(ex)

    db.session.commit()

    print('◉ 시드 데이터 생성 완료')
    print(' ✦ 관리자: admin@sasa.hs.kr / admin1234')
    print(' ✦ 학생: guest@sasa.hs.kr / guest1234')


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