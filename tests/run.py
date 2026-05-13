import os
from app import create_app, db
from app.models import User, Penalty, Document, Exemption, PenaltyStandard
from datetime import date, timedelta

app = create_app(os.environ.get('FLASK_ENV', 'development'))

# 벌점 기준표 (단일 소스 오브 트루스)
STANDARDS_DATA = [
    ('생활규정', '아침 점호 지각 / 오전 시까지 미등교 / 저녁 점호 불참', 1, 0),
    ('생활규정', '호실 청결 상태 불량', 1, 0),
    ('생활규정', '학습 시간 지각 / 무단 이석', 1, 0),
    ('생활규정', '귀사 시간 미준수 및 귀가 신고 불이행', 2, 0),
    ('생활규정', '소란 행위 / 취침 방해 / 특별한 사유 없이 취침 시간에 호실 밖에 있는 경우', 2, 0),
    ('생활규정', '기숙사 내 허용되지 않은 음식물 및 물품 반입', 2, 0),
    ('생활규정', '휴게실 이외의 장소에서 취식 / 시간 미준수', 2, 0),
    ('생활규정', '사전 신고 없이 자습 시간 중 호실 취침', 2, 0),
    ('생활규정', '타 호실 무단 출입 및 타 호실 취침', 3, 0),
    ('생활규정', '학습 공간에서 학습과 관계없는 행위 (게임, 드라마 시청 등)', 3, 0),
    ('생활규정', '기숙사 무단 출입 및 방조', 3, 0),
    ('생활규정', '사감의 정당한 지시 불이행 (비명시 항목)', 5, 0),
    ('생활규정', '사감의 승인 없이 배달음식을 기숙사에 반입 및 섭취', 5, 0),
    ('생활규정', '무단 외출 (기숙사동에서 이탈)', 5, 0),
    ('생활규정', '상기 내용에 포함되지 않은 사안 (생활교육위원회 회부 시 벌점 5점)', 1, 0),
]


def sync_standards():
    """
    벌점 기준표를 항상 최신 상태로 동기화.
    - (category, description) 조합을 기준 키로 사용
    - 없으면 INSERT, 있으면 points가 다를 때만 UPDATE
    - STANDARDS_DATA에 없는 기존 레코드는 건드리지 않음 (삭제 원할 시 별도 처리)
    """
    updated = 0
    created = 0

    for cat, desc, pts, merit in STANDARDS_DATA:
        existing = PenaltyStandard.query.filter_by(
            category=cat, description=desc
        ).first()

        if existing is None:
            db.session.add(PenaltyStandard(
                category=cat,
                description=desc,
                penalty_points=pts,
                merit_points=merit,
            ))
            created += 1
        else:
            # 점수가 변경됐을 때만 업데이트
            if existing.penalty_points != pts or existing.merit_points != merit:
                existing.penalty_points = pts
                existing.merit_points = merit
                updated += 1

    db.session.commit()
    print(f'벌점 기준표 동기화 완료 — 신규: {created}건, 업데이트: {updated}건')


def seed_users_and_test_data():
    """최초 1회만 실행되는 테스트 데이터 (유저가 이미 있으면 스킵)"""
    if User.query.first():
        print('ⓘ 유저 데이터가 이미 존재하여 테스트 시드를 스킵합니다.')
        return

    # 관리자 계정
    admin = User(
        email='admin@sasa.hs.kr',
        name='관리자',
        student_id='00000000',
        room_number='관리실',
        is_admin=True,
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
        grade=1,
    )
    student.password = 'student1234'
    db.session.add(student)

    db.session.flush()  # ID 생성

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
    print('✅ 테스트 시드 데이터 생성 완료')
    print('📌 관리자: admin@sasa.hs.kr / admin1234')
    print('📌 학생:   20231001@sasa.hs.kr / student1234')


def seed_db():
    """전체 시드 진입점"""
    sync_standards()  # 항상 실행
    seed_users_and_test_data()  # 최초 1회만


@app.cli.command('seed')
def seed_command():
    """DB 시드 데이터 생성: flask seed"""
    with app.app_context():
        db.create_all()
        seed_db()


@app.cli.command('sync-standards')
def sync_standards_command():
    """벌점 기준표만 단독 동기화: flask sync-standards"""
    with app.app_context():
        sync_standards()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_db()
    app.run(debug=True, host='0.0.0.0', port=5000)