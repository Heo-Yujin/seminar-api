미니과제 지시서 
세미나룸 예약 API(mini) — Git 조직 관리 + Docker 볼륨
1. 프로젝트 개요 및 목표
이름: seminar-api
목표:
Flask + MariaDB + Docker + GitHub Actions CI/CD로 세미나룸 예약 API를 구현한다.
Git 전략: main(릴리즈)과 devA, devB 브랜치로 나누고, devA/devB → main 머지한다.
DB 데이터는 Docker 볼륨으로 영속화하여 컨테이너 재시작 시에도 유지된다.

팀 구성: 2 명
A: API + DB 구조 (devA githubID<HeoYujin>)
B: Docker + CI/CD (devB githubID<BlakeEdenParker>)

2. Git 조직 관리 및 브랜치 전략
브랜치 구조
main: 최종 릴리즈 브랜치. 배포 기준 코드.
devA: A 의 개발 브랜치. API + DB 관련 기능.
devB: B 의 개발 브랜치. Docker + CI/CD 관련 기능.
규칙
로컬에서는 항상 브랜치별 작업:
A: git checkout devA → 작업 → devA 푸시
B: git checkout devB → 작업 → devB 푸시
unstable 한 코드는 main 에 직접 푸시하지 않는다.
기능이 정리되면 Pull Request로 devA → main, devB → main 머지한다.
main 병합 후에는 배포 워크플로가 자동 실행된다GitHub(Actions).
실제 플로우

A: devA --PR--> main --(deploy)--> 서버
B: devB --PR--> main --(deploy)--> 서버
main 으로 PR 을 보내면 코드 리뷰 후 머지.
main 푸시 → CI(테스트) → CD(배포) 자동.

3. 요구사항 
핵심 기능
세미나룸 관리
GET /api/rooms
GET /api/rooms/<id>
POST /api/rooms
PUT /api/rooms/<id>
DELETE /api/rooms/<id>
예약 관리
GET /api/reservations
쿼리: room_id, date 필터 지원
POST /api/reservations
DELETE /api/reservations/<id>
헬스체크
GET /health → {"status":"ok"}
응답 형식
목록 조회는 {"items": [...], "count": N} 비슷하게 반환한다.

4. 데이터베이스 설계 (Vol ume 영속화 포함)
DB명: seminar_db
테이블 1: rooms

CREATE TABLE rooms (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  capacity INT NOT NULL,
  equipment VARCHAR(255) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
테이블 2: reservations

CREATE TABLE reservations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  room_id INT NOT NULL,
  user_name VARCHAR(100) NOT NULL,
  user_email VARCHAR(100) NOT NULL,
  date DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  purpose VARCHAR(255) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_reservations_room
    FOREIGN KEY (room_id) REFERENCES rooms(id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
Docker 볼륨 전략
MariaDB 데이터 디렉터리를 외부 볼륨으로 마운트한다.
컨테이너 삭제/재생성 시에도 데이터가 유지된다.
docker-compose.yml 에서 다음처럼 정의:

volumes:
  seminar_data:
db 서비스: volumes: - seminar_data:/var/lib/mysql
→ MariaDB 데이터가 seminar_data 볼륨에 영속화된다.

5. API 명세 
5.1. 세미나룸
GET /api/rooms → {"items": [...], "count": N}
GET /api/rooms/<id> → 단건
POST /api/rooms → {name, capacity, equipment} → {"id":..., "message":"created"}
PUT /api/rooms/<id> → 수정 → {"id":..., "message":"updated"}
DELETE /api/rooms/<id> → {"id":..., "message":"deleted"}
5.2. 예약
GET /api/reservations?room_id=1&date=2026-06-03 → {"items":[...], "count":N}
POST /api/reservations → {room_id, user_name, user_email, date, start_time, end_time, purpose} → {"id":..., "message":"reserved"}
DELETE /api/reservations/<id> → {"id":..., "message":"cancelled"}
5.3. 헬스체크
GET /health → {"status":"ok"}

6. 기술 스택
Python 3.12
Flask
MariaDB 10.6
mariadb(Python Connector) 또는 sqlalchemy + mysql-connector
Gunicorn
Docker + Docker Compose
GitHub Actions(ubuntu-latest)
SSH 배포 (GitHub Secrets: SERVER_HOST, SERVER_USER, SERVER_SSH_KEY)

7. 프로젝트 구조

seminar-api/
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ db.py
│  └─ routes.py
├─ migrations/
│  └─ 001_init.sql
├─ tests/
│  └─ test_api.py
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
├─ .env.example
├─ README.md
└─ .github/
   └─ workflows/
      └─ ci-cd.yml

8. 역할 분담 (브랜치 기준)
A(API + DB, devA)
브랜치: devA 주인
DB 스키마(migrations/001_init.sql) 작성
Flask 앱 구조: app/__init__.py, config.py, db.py, routes.py
/api/rooms CRUD, /api/reservations CRUD, /health 구현
tests/test_api.py 작성
devA → main 머지 요청
B(Docker + CI/CD, devB)
브랜치: devB 주인
Dockerfile, docker-compose.yml 작성
requirements.txt 정리
.github/workflows/ci-cd.yml 작성(테스트 → 빌드 → SSH 배포)
서버 환경 설정(Docker, docker-compose, SSH 키)
devB → main 머지 요청

9. 구현 단계
조직 + 저장소 + 브랜치 생성
GitHub 조직 생성(또는 기존 조직 사용)
조직에서 새 리포지토리: seminar-api 생성
브랜치 전략 설정:
main 을 기본 브랜치로 설정
main 브랜치 보호 규칙:
"Require a pull request before merging" ON
"Require approvals" 1 명 이상
로컬 clone:

git clone https://github.com/<ORG_OR_USER>/seminar-api.git
cd seminar-api
git checkout -b devA   # A
git checkout -b devB   # B
A 는 devA, B 는 devB 에서 작업.

