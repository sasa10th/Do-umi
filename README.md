# Do-umi
CS Project in Sejong Academy of Science and Arts<br>
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

> **"열심히 살자"** - TEAM 2 (신재민, 김지환, 김민기)

기숙사 벌점 부과 사실을 실시간으로 알리고, 행정 업무를 디지털화하여 학생의 행동 교정을 돕는 웹앱 서비스이다.

---

## 1. 프로젝트 배경 및 목적
* **문제 배경**: 실시간 알림 부재로 인한 벌점 인지 지연 및 반복적인 벌점 누적.
* **핵심 목표**: 정보 접근성 개선, 행정적 비효율성 제거, 체계적인 스케줄링 관리.

## 2. 핵심 기능
### 벌점 변동 알림 서비스
* 벌점/상점 부여 시 즉각적인 알림 제공 (전화번호 등록 시 SMS, 미등록 시 SASA 메일 발송).

### 비대면 전자서명 시스템
* 기존 수기 서명 방식을 대체하여 웹상에서 벌점 확인 및 천자문 제출 시 본인 인증 서명 첨부.

### 천자문 스케줄링 관리
* 대시보드 내 천자문 마감 기한 표시 및 시험 기간 자동 연기 로직 적용.

### 면제권 시스템 (추가 기능)
* 일정 기간(30일/45일) 무벌점 시 면제권 자동 지급 및 사용 기능.

## 3. 기술 스택 및 도구
* **Language**: Korean, English
* **Backend**: Flask (Python) 
* **Tool**: Visual Studio Code, LLM
* **Process Model**: V 모델 (신뢰성 확보를 위한 1:1 테스트 대응)

---

## 4. 프로젝트 구조
Do-u-mi/
├── app/
│   ├── __init__.py         # 앱 팩토리 (create_app 패턴 권장)
│   ├── models.py           # DB 모델
│   ├── auth.py             # 인증 로직 (Blueprint)
│   ├── routes.py           # 페이지 라우팅 (Blueprint)
│   ├── api.py              # JSON API 엔드포인트 (필요 시)
│   └── utils/
│       ├── __init__.py
│       ├── mail.py         # 이메일 발송
│       ├── sms.py          # SMS 발송
│       └── signature.py    # 전자서명 처리
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_models.py
│   └── test_routes.py
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── templates/
│   ├── base.html           # 공통 레이아웃
│   ├── auth/
│   │   ├── login.html
│   │   └── signup.html
│   └── dashboard/
│       ├── index.html
│       ├── penalty.html
│       └── document.html
├── migrations/             # Flask-Migrate DB 마이그레이션
├── .env
├── .gitignore
├── config.py               # 환경별 설정 클래스 (Dev/Prod/Test)
├── README.md
└── requirements.txt
