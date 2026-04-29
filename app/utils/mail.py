from flask import current_app, render_template_string
from flask_mail import Message
from .. import mail


PENALTY_TEMPLATE = """
안녕하세요, {{ student.name }}님.

[Do우미 벌점 알림]

벌점이 부과되었습니다.

- 일자: {{ penalty.date }}
- 분류: {{ penalty.category }}
- 사유: {{ penalty.reason }}
- 부과 점수: {{ penalty.points }}점
- 현재 누적 벌점: {{ student.total_penalty_points }}점
- 현재 단계: {{ student.stage }}단계

벌점 내역 확인 및 전자서명은 Do우미 시스템에서 진행해주세요.

이 메일은 자동으로 발송된 메일입니다.
"""

MERIT_TEMPLATE = """
안녕하세요, {{ student.name }}님.

[Do우미 상점 알림]

상점이 부여되었습니다.

- 일자: {{ penalty.date }}
- 분류: {{ penalty.category }}
- 사유: {{ penalty.reason }}
- 부여 상점: {{ penalty.merit_points }}점

Do우미 시스템에서 상세 내역을 확인하세요.
"""


def send_penalty_notification(student, penalty):
    """벌점/상점 부과 이메일 알림"""
    if not student.email:
        return

    try:
        if penalty.points > 0:
            subject = f'[Do우미] 벌점 부과 알림 - {penalty.points}점'
            body = render_template_string(PENALTY_TEMPLATE, student=student, penalty=penalty)
        else:
            subject = f'[Do우미] 상점 부여 알림 - {penalty.merit_points}점'
            body = render_template_string(MERIT_TEMPLATE, student=student, penalty=penalty)

        msg = Message(
            subject=subject,
            recipients=[student.email],
            body=body
        )
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f'메일 발송 실패: {e}')


def send_document_deadline_reminder(student, document):
    """천자문 기한 알림"""
    if not student.email:
        return

    try:
        body = f"""
안녕하세요, {student.name}님.

[Do우미 천자문 기한 알림]

다음 천자문 제출 기한이 다가왔습니다.

- 제목: {document.title}
- 기한: {document.due_date}
- 남은 일수: {document.days_remaining}일

기한 내 제출 및 면제권 사용은 Do우미 시스템에서 가능합니다.
"""
        msg = Message(
            subject=f'[Do우미] 천자문 기한 알림 - {document.days_remaining}일 남음',
            recipients=[student.email],
            body=body
        )
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f'메일 발송 실패: {e}')