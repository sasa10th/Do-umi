# Do-umi
CS Project in Sejong Academy of Science and Arts<br>
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

> [cite_start]**"열심히 살자"** - TEAM 2 (신재민, 김지환, 김민기) [cite: 7]

[cite_start]기숙사 벌점 부과 사실을 실시간으로 알리고, 행정 업무를 디지털화하여 학생의 행동 교정을 돕는 웹앱 서비스입니다. [cite: 19, 69]

---

## 1. 프로젝트 배경 및 목적 🎯
* [cite_start]**문제 배경**: 실시간 알림 부재로 인한 벌점 인지 지연 및 반복적인 벌점 누적[cite: 10, 11].
* [cite_start]**핵심 목표**: 정보 접근성 개선, 행정적 비효율성 제거, 체계적인 스케줄링 관리[cite: 15, 16, 17].

## 2. 핵심 기능 🛠️
### 🔔 벌점 변동 알림 서비스
* [cite_start]벌점/상점 부여 시 즉각적인 알림 제공 (전화번호 등록 시 SMS, 미등록 시 SASA 메일 발송)[cite: 71, 72].

### 📝 비대면 전자서명 시스템
* [cite_start]기존 수기 서명 방식을 대체하여 웹상에서 벌점 확인 및 천자문 제출 시 본인 인증 서명 첨부[cite: 76, 78].

### 📅 천자문 스케줄링 관리
* [cite_start]대시보드 내 천자문 마감 기한 표시 및 시험 기간 자동 연기 로직 적용[cite: 73, 75].

### 🎟️ 면제권 시스템 (추가 기능)
* [cite_start]일정 기간(30일/45일) 무벌점 시 면제권 자동 지급 및 사용 기능[cite: 157, 182].

## 3. 기술 스택 및 도구 💻
* [cite_start]**Language**: Korean, English [cite: 80]
* [cite_start]**Backend**: Node.js 또는 Flask (Python) 
* [cite_start]**Tool**: Visual Studio Code, LLM [cite: 82]
* [cite_start]**Process Model**: V 모델 (신뢰성 확보를 위한 1:1 테스트 대응) [cite: 90, 93]

## 4. 요구사항 및 진행 현황 ✅
| ID | 기능명 | 우선순위 | 상태 |
| :--- | :--- | :---: | :---: |
| FR-02 | 어드민 계정 구현 | 상 | [cite_start]반영 예정 [cite: 105] |
| FR-04 | 면제권 사용 (천자문 제거) | 상 | [cite_start]반영 예정 [cite: 105] |
| NFR-02 | 비밀번호 암호화(해시) | 상 | [cite_start]반영 예정 [cite: 110] |

---

## 5. 팀원 역할 👥
* [cite_start]**신재민**: 구조 설계 / 계획 / 아이디어 [cite: 4]
* [cite_start]**김지환**: 기능 구현 [cite: 5]
* [cite_start]**김민기**: 계획 / 자료 정리 [cite: 6]
