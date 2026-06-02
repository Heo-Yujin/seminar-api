import os

class Config:
    # 도커 환경에서는 DB_HOST가 'db' (docker-compose 서비스 이름)가 됩니다.
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "rootpassword")
    DB_NAME = os.getenv("DB_NAME", "seminar_db")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    
    # JSON 응답 시 한글 깨짐 방지
    JSON_AS_ASCII = False