"""
전자서명 처리 유틸리티
Canvas에서 그린 서명을 base64로 받아 저장/검증합니다.
"""
import base64
import re
from datetime import datetime


def validate_signature(signature_data: str) -> bool:
    """
    전자서명 데이터 유효성 검사.
    base64 인코딩된 PNG 이미지 데이터여야 합니다.
    """
    if not signature_data:
        return False

    # data:image/png;base64,... 형식 확인
    pattern = r'^data:image/(png|jpeg|jpg);base64,[A-Za-z0-9+/]+=*$'
    if not re.match(pattern, signature_data):
        return False

    # 최소 크기 확인 (너무 짧으면 빈 서명)
    b64_part = signature_data.split(',')[1] if ',' in signature_data else ''
    if len(b64_part) < 100:
        return False

    return True


def get_signature_metadata(signature_data: str) -> dict:
    """서명 데이터에서 메타데이터 추출"""
    if not validate_signature(signature_data):
        return {}

    b64_part = signature_data.split(',')[1]
    byte_size = len(base64.b64decode(b64_part))

    return {
        'format': 'PNG',
        'byte_size': byte_size,
        'created_at': datetime.utcnow().isoformat(),
    }


def create_signature_record(user_id: int, signature_data: str, purpose: str = '') -> dict:
    """서명 레코드 생성 (DB 저장용 딕셔너리 반환)"""
    if not validate_signature(signature_data):
        raise ValueError('유효하지 않은 서명 데이터입니다.')

    metadata = get_signature_metadata(signature_data)
    return {
        'user_id': user_id,
        'signature_data': signature_data,
        'purpose': purpose,
        'metadata': metadata,
        'signed_at': datetime.utcnow(),
    }