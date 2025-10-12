# app.py
import os
from flask import Flask, jsonify
from flasgger import Swagger
from api.routes import bp as api_bp
from utils.db import get_client
from werkzeug.exceptions import HTTPException

def create_app():
    app = Flask(__name__)
    app.config["SWAGGER"] = {
        "title": "TCS Vulnerability Testcases API",
        "uiversion": 3
    }
    Swagger(app)

    # register blueprint
    app.register_blueprint(api_bp)

    # health endpoint
    @app.route("/health", methods=["GET"])
    def health():
        try:
            get_client().admin.command("ping")
            return jsonify({"status": "ok"}), 200
        except Exception:
            return jsonify({"status": "unhealthy"}), 503

    @app.errorhandler(Exception)
    def handle_error(e):
        if isinstance(e, HTTPException):
            return jsonify({"error": e.description}), e.code
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host=host, port=port)
