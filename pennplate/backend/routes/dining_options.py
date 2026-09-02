from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from backend.routes.utils import menu_filters_from_request, parse_sort
from backend.services.filtering import build_dining_option, sort_dining_options


bp = Blueprint("dining_options", __name__)


@bp.get("/api/dining-options")
def dining_options():
    filters = menu_filters_from_request(request, require_hall=False)
    sort = parse_sort(request.args.get("sort"))
    db = current_app.config["DB_CLIENT"]
    halls = db.list_halls()
    options = []

    for hall in halls:
        rows = db.menu_items(hall["id"], filters.date, filters.meal)
        if not rows:
            continue
        hall_filters = filters if filters.hall else filters.__class__(**{**filters.__dict__, "hall": hall["slug"]})
        options.append(build_dining_option(hall, rows, hall_filters))

    return jsonify(
        {
            "date": filters.date,
            "meal": filters.meal,
            "options": sort_dining_options(options, sort),
        }
    )
