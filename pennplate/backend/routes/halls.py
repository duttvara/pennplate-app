from __future__ import annotations

from flask import Blueprint, current_app, jsonify


bp = Blueprint("halls", __name__)


@bp.get("/api/halls")
def halls():
    db = current_app.config["DB_CLIENT"]
    return jsonify({"halls": db.list_halls()})
