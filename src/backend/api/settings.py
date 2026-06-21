from flask import Blueprint, current_app, jsonify, request

bp = Blueprint("settings", __name__, url_prefix="/api/settings")


def public_settings(settings):
    return {
        key: value
        for key, value in settings.items()
        if key != "api_key"
    } | {"api_key_configured": bool(settings.get("api_key"))}


@bp.get("")
def get_settings():
    settings = current_app.config["REPOSITORY"].settings()
    return jsonify(public_settings(settings))


@bp.put("")
def save_settings():
    settings = current_app.config["REPOSITORY"].save_settings(request.get_json() or {})
    return jsonify(public_settings(settings))


@bp.post("/test")
def test_connection():
    settings = current_app.config["REPOSITORY"].settings()
    configured = bool(settings.get("api_key"))
    return jsonify(
        {
            "ok": configured,
            "message": "AI configuration is ready." if configured else "AI is not configured. Add API settings before starting analysis.",
        }
    )
