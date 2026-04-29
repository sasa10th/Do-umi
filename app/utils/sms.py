"""
SMS 발송 유틸리티
실제 사용 시 CoolSMS, 네이버 클라우드 SMS 등의 API키를 .env에 등록하세요.
"""
import os
from flask import current_app


def send_sms(phone: str, message: str) -> bool:
    """
    SMS 발송 함수.
    환경변수 SMS_PROVIDER에 따라 실제 발송 로직을 구현하세요.
    현재는 콘솔 출력(개발 모드)으로 동작합니다.
    """
    if not phone:
        return False

    provider = os.environ.get('SMS_PROVIDER', 'console')

    if provider == 'console':
        current_app.logger.info(f'[SMS 개발모드] TO: {phone} | MSG: {message}')
        return True

    elif provider == 'coolsms':
        # CoolSMS API 연동 예시
        try:
            import coolsms  # pip install coolsms
            api_key = os.environ.get('COOLSMS_API_KEY')
            api_secret = os.environ.get('COOLSMS_API_SECRET')
            sender = os.environ.get('COOLSMS_SENDER', '01000000000')
            # coolsms 라이브러리 사용법에 따라 구현
            current_app.logger.info(f'CoolSMS 발송: {phone}')
            return True
        except Exception as e:
            current_app.logger.error(f'CoolSMS 발송 실패: {e}')
            return False

    return False


def send_penalty_sms(student, penalty):
    """벌점 부과 SMS 알림"""
    if not student.phone:
        return False

    if penalty.points > 0:
        msg = (f'[Do우미] {student.name}님 벌점 {penalty.points}점 부과. '
               f'사유: {penalty.reason}. '
               f'누적 벌점: {student.total_penalty_points}점')
    else:
        msg = (f'[Do우미] {student.name}님 상점 {penalty.merit_points}점 부여. '
               f'사유: {penalty.reason}.')

    return send_sms(student.phone, msg)


def send_document_sms(student, document):
    """천자문 기한 SMS 알림"""
    if not student.phone:
        return False

    msg = (f'[Do우미] {student.name}님 천자문 기한 알림. '
           f'"{document.title}" 제출 기한: {document.due_date} '
           f'({document.days_remaining}일 남음)')

    return send_sms(student.phone, msg)