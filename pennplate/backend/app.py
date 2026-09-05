from __future__ import annotations

import sys
import os
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import ConfigError
from backend.routes.dining_options import bp as dining_options_bp
from backend.routes.halls import bp as halls_bp
from backend.routes.menu import bp as menu_bp
from backend.routes.utils import BadRequest
from backend.services.database import SupabaseReadClient

ALLOWED_DEV_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
}


def allowed_origins() -> set[str]:
    configured = os.environ.get("FRONTEND_ORIGINS", "")
    return ALLOWED_DEV_ORIGINS | {
        origin.strip().rstrip("/")
        for origin in configured.split(",")
        if origin.strip()
    }


def create_app(db_client=None) -> Flask:
    app = Flask(__name__)
    app.config["DB_CLIENT"] = db_client or SupabaseReadClient()

    app.register_blueprint(halls_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(dining_options_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.after_request
    def add_cors_headers(response):
        request_origin = request.headers.get("Origin")
        origins = allowed_origins()

        response.headers["Access-Control-Allow-Origin"] = (
            request_origin if request_origin in origins else "http://localhost:5173"
        )
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        return response

    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return jsonify({"error": str(error)}), 400

    @app.errorhandler(ConfigError)
    def handle_config_error(error):
        return jsonify({"error": str(error)}), 500

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled API error")
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=True)
