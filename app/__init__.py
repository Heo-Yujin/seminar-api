# app/__init__.py
from flask import Flask
from app.config import Config
from app.db import close_db
from app.routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 블루프린트 등록
    app.register_blueprint(api_bp)
    
    # 앱 컨텍스트 종료 시 DB 연결 해제 등록
    app.teardown_appcontext(close_db)
    
    return app