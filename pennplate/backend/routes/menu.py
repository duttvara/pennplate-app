from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from backend.routes.utils import BadRequest, menu_filters_from_request
from backend.services.filtering import build_menu_response


bp = Blueprint("menu", __name__)


@bp.get("/api/menu")
def menu():
    filters = menu_filters_from_request(request)
    db = current_app.config["DB_CLIENT"]
    hall = db.get_hall_by_slug(filters.hall)
    if hall is None:
        raise BadRequest(f"Unknown dining hall: {filters.hall}")

    rows = db.menu_items(hall["id"], filters.date, filters.meal)
    return jsonify(build_menu_response(hall, rows, filters))
