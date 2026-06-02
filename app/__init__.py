# app/__init__.py
from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from app.config import Config
from app.db import close_db
from app.routes import api_bp

try:
    from flask_cors import CORS
except ImportError:
    CORS = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Cloudflare + Nginx 프록시 체인: x_for=2 (Cloudflare + Nginx)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2, x_proto=1, x_host=1)

    if CORS:
        CORS(app)
    app.register_blueprint(api_bp)
    app.teardown_appcontext(close_db)

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": str(e.description)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": str(e.description)}), 404

    @app.errorhandler(409)
    def conflict(e):
        return jsonify({"error": str(e.description)}), 409

    return app
