FROM python:3.12-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

EXPOSE 8000

# Gunicorn으로 Flask 앱 실행 (app 모듈의 app 객체 실행)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]