from flask import Blueprint, current_app, jsonify, request

bp = Blueprint("packets", __name__, url_prefix="/api/captures/<int:capture_id>")


@bp.get("/packets")
def list_packets(capture_id):
    return jsonify(current_app.config["REPOSITORY"].list_packets(capture_id, request.args))


@bp.get("/packets/<int:number>")
def get_packet(capture_id, number):
    packet = current_app.config["REPOSITORY"].get_packet(capture_id, number)
    return (jsonify(packet), 200) if packet else (jsonify({"error": "Packet not found"}), 404)
