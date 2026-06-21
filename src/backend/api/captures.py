from pathlib import Path
from threading import Thread

from flask import Blueprint, current_app, jsonify, request, send_file

from src.backend.services.capture_analyzer import CaptureAnalyzer
from src.backend.services.file_storage import FileStorage

bp = Blueprint("captures", __name__, url_prefix="/api/captures")


def repo():
    return current_app.config["REPOSITORY"]


def public_capture(capture):
    if not capture:
        return None
    return {key: value for key, value in capture.items() if key != "stored_path"}


def start_analysis(capture_id):
    repo().update_status(capture_id, "Analyzing")
    Thread(target=CaptureAnalyzer(repo()).analyze, args=(capture_id,), daemon=True).start()


@bp.get("")
def list_captures():
    captures = repo().list_captures(request.args.get("q", ""), request.args.get("status", ""))
    return jsonify([public_capture(capture) for capture in captures])


@bp.post("")
def upload_capture():
    upload = request.files.get("file")
    if not upload:
        return jsonify({"error": "Upload failed. Choose a PCAP or PCAPNG file."}), 400
    try:
        storage = FileStorage(Path(current_app.config["DATA_DIR"]) / "captures")
        saved = storage.save(upload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    capture_id = repo().create_capture(**saved)
    start_analysis(capture_id)
    return jsonify(public_capture(repo().get_capture(capture_id))), 201


@bp.get("/<int:capture_id>")
def get_capture(capture_id):
    capture = repo().get_capture(capture_id)
    return (jsonify(public_capture(capture)), 200) if capture else (jsonify({"error": "Capture not found"}), 404)


@bp.post("/<int:capture_id>/retry")
def retry_capture(capture_id):
    start_analysis(capture_id)
    return jsonify(public_capture(repo().get_capture(capture_id)))


@bp.get("/<int:capture_id>/download")
def download_capture(capture_id):
    capture = repo().get_capture(capture_id)
    if not capture:
        return jsonify({"error": "Capture not found"}), 404
    return send_file(capture["stored_path"], as_attachment=True, download_name=capture["original_name"])


@bp.delete("/<int:capture_id>")
def delete_capture(capture_id):
    capture = repo().delete_capture(capture_id)
    if capture:
        Path(capture["stored_path"]).unlink(missing_ok=True)
    return jsonify({"ok": True})
