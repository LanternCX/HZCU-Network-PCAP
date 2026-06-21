from flask import Blueprint, Response, current_app, jsonify

from src.backend.services.ai_summary import context_preview, stream_summary

bp = Blueprint("ai", __name__, url_prefix="/api/captures/<int:capture_id>/ai")


@bp.get("/context")
def ai_context(capture_id):
    return jsonify(context_preview(current_app.config["REPOSITORY"], capture_id))


@bp.get("/summary")
def ai_summary(capture_id):
    repository = current_app.config["REPOSITORY"]

    def body():
        for chunk in stream_summary(repository, capture_id):
            yield chunk

    return Response(body(), mimetype="text/markdown")
