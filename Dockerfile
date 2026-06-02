FROM python:3.12-slim

WORKDIR /app

# ★ 핵심 추가: MariaDB 파이썬 패키지 설치를 위한 리눅스 시스템 도구 설치
RUN apt-get update && \
    apt-get install -y gcc pkg-config libmariadb-dev libmariadb-dev-compat && \
    rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# Gunicorn으로 앱 실행
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app()"]