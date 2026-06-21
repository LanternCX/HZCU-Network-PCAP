from flask import Blueprint, current_app, jsonify

bp = Blueprint("statistics", __name__, url_prefix="/api/statistics")


@bp.get("")
def dashboard_stats():
    return jsonify(current_app.config["REPOSITORY"].stats())


@bp.get("/captures/<int:capture_id>")
def capture_stats(capture_id):
    return jsonify(current_app.config["REPOSITORY"].stats(capture_id))
