from pathlib import Path
from io import BytesIO
from time import sleep, monotonic

from src.backend.app import create_app
from src.backend.db.repository import Repository
from src.backend.services import ai_summary
from src.backend.services.capture_analyzer import CaptureAnalyzer


def test_upload_rejects_unsupported_file(tmp_path):
    app = create_app({"DATA_DIR": tmp_path, "TESTING": True})

    with app.test_client() as client:
        response = client.post(
            "/api/captures",
            data={"file": (Path(__file__).open("rb"), "notes.txt")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    assert "Unsupported file type" in response.get_json()["error"]


def test_missing_tshark_marks_capture_failed(tmp_path):
    repo = Repository(tmp_path / "app.sqlite")
    capture_id = repo.create_capture(
        original_name="demo.pcapng",
        stored_path=str(tmp_path / "demo.pcapng"),
        file_size=128,
        file_type="PCAPNG",
    )

    analyzer = CaptureAnalyzer(repo, tshark_path=None)
    analyzer.analyze(capture_id)

    capture = repo.get_capture(capture_id)
    assert capture["status"] == "Failed"
    assert "tshark is required" in capture["error_message"]


def test_packets_endpoint_filters_sorts_and_paginates(tmp_path):
    repo = Repository(tmp_path / "app.sqlite")
    capture_id = repo.create_capture(
        original_name="demo.pcapng",
        stored_path=str(tmp_path / "demo.pcapng"),
        file_size=128,
        file_type="PCAPNG",
    )
    repo.save_analysis(
        capture_id,
        [
            {
                "number": 1,
                "timestamp": "2026-06-21T10:00:00",
                "src_ip": "10.0.0.2",
                "src_port": "51514",
                "dst_ip": "8.8.8.8",
                "dst_port": "53",
                "protocol": "DNS",
                "length": 74,
                "details": {"Frame": {"Length": "74 bytes"}},
            },
            {
                "number": 2,
                "timestamp": "2026-06-21T10:00:02",
                "src_ip": "10.0.0.3",
                "src_port": "443",
                "dst_ip": "10.0.0.2",
                "dst_port": "51514",
                "protocol": "TCP",
                "length": 1514,
                "details": {"Frame": {"Length": "1514 bytes"}},
            },
        ],
    )
    app = create_app({"DATA_DIR": tmp_path, "TESTING": True})

    with app.test_client() as client:
        response = client.get(
            f"/api/captures/{capture_id}/packets",
            query_string={
                "q": "10.0.0.2",
                "sort": "length",
                "direction": "desc",
                "page": 1,
                "page_size": 1,
            },
        )

    body = response.get_json()
    assert response.status_code == 200
    assert body["total"] == 2
    assert body["items"][0]["number"] == 2


def test_ai_context_never_includes_raw_capture_path(tmp_path):
    repo = Repository(tmp_path / "app.sqlite")
    capture_id = repo.create_capture(
        original_name="demo.pcapng",
        stored_path=str(tmp_path / "private-demo.pcapng"),
        file_size=128,
        file_type="PCAPNG",
    )
    repo.save_analysis(
        capture_id,
        [
            {
                "number": 1,
                "timestamp": "2026-06-21T10:00:00",
                "src_ip": "10.0.0.2",
                "src_port": "51514",
                "dst_ip": "8.8.8.8",
                "dst_port": "53",
                "protocol": "DNS",
                "length": 74,
                "details": {"DNS": {"Query": "example.com"}},
            }
        ],
    )
    app = create_app({"DATA_DIR": tmp_path, "TESTING": True})

    with app.test_client() as client:
        response = client.get(f"/api/captures/{capture_id}/ai/context")

    body = response.get_json()
    assert response.status_code == 200
    assert "private-demo.pcapng" not in str(body)
    assert body["packet_sample"][0]["protocol"] == "DNS"


def test_capture_api_does_not_expose_stored_file_path(tmp_path):
    repo = Repository(tmp_path / "app.sqlite")
    repo.create_capture(
        original_name="demo.pcapng",
        stored_path=str(tmp_path / "private-demo.pcapng"),
        file_size=128,
        file_type="PCAPNG",
    )
    app = create_app({"DATA_DIR": tmp_path, "TESTING": True})

    with app.test_client() as client:
        response = client.get("/api/captures")

    body = response.get_json()
    assert response.status_code == 200
    assert "stored_path" not in body[0]
    assert "private-demo.pcapng" not in str(body)


def test_upload_returns_before_analysis_finishes(tmp_path, monkeypatch):
    def slow_analysis(self, capture_id):
        sleep(0.5)

    monkeypatch.setattr(CaptureAnalyzer, "analyze", slow_analysis)
    app = create_app({"DATA_DIR": tmp_path, "TESTING": True})

    started = monotonic()
    with app.test_client() as client:
        response = client.post(
            "/api/captures",
            data={"file": (BytesIO(b"pcap"), "demo.pcapng")},
            content_type="multipart/form-data",
        )
    elapsed = monotonic() - started

    assert response.status_code == 201
    assert elapsed < 0.3


def test_settings_accept_api_key_without_returning_it(tmp_path):
    app = create_app({"DATA_DIR": tmp_path, "TESTING": True})

    with app.test_client() as client:
        response = client.put(
            "/api/settings",
            json={"api_base": "https://api.deepseek.com", "model": "deepseek-v4-pro", "api_key": "secret"},
        )
        saved = response.get_json()
        checked = client.post("/api/settings/test").get_json()

    assert response.status_code == 200
    assert "api_key" not in saved
    assert saved["api_key_configured"] is True
    assert checked["ok"] is True


def test_non_streaming_ai_summary_returns_text(tmp_path, monkeypatch):
    repo = Repository(tmp_path / "app.sqlite")
    capture_id = repo.create_capture(
        original_name="demo.pcapng",
        stored_path=str(tmp_path / "demo.pcapng"),
        file_size=128,
        file_type="PCAPNG",
    )
    repo.save_settings({"api_key": "secret", "streaming": "false"})
    repo.save_analysis(
        capture_id,
        [
            {
                "number": 1,
                "timestamp": "2026-06-21T10:00:00",
                "src_ip": "10.0.0.2",
                "src_port": "51514",
                "dst_ip": "8.8.8.8",
                "dst_port": "53",
                "protocol": "DNS",
                "length": 74,
                "details": {"DNS": {"Query": "example.com"}},
            }
        ],
    )

    def fake_completion(**kwargs):
        assert kwargs["stream"] is False
        return {"choices": [{"message": {"content": "Summary text"}}]}

    monkeypatch.setattr(ai_summary, "completion", fake_completion)

    assert "".join(ai_summary.stream_summary(repo, capture_id)) == "Summary text"
    assert repo.get_ai_summary(capture_id)["summary"] == "Summary text"


def test_ai_summary_route_streams_without_context_error(tmp_path):
    repo = Repository(tmp_path / "app.sqlite")
    capture_id = repo.create_capture(
        original_name="demo.pcapng",
        stored_path=str(tmp_path / "demo.pcapng"),
        file_size=128,
        file_type="PCAPNG",
    )
    repo.save_analysis(
        capture_id,
        [
            {
                "number": 1,
                "timestamp": "2026-06-21T10:00:00",
                "src_ip": "10.0.0.2",
                "src_port": "51514",
                "dst_ip": "8.8.8.8",
                "dst_port": "53",
                "protocol": "DNS",
                "length": 74,
                "details": {"DNS": {"Query": "example.com"}},
            }
        ],
    )
    app = create_app({"DATA_DIR": tmp_path, "TESTING": True})

    with app.test_client() as client:
        response = client.get(f"/api/captures/{capture_id}/ai/summary")

    assert response.status_code == 200
    assert b"AI is not configured" in response.data


def test_ai_context_returns_saved_summary(tmp_path):
    repo = Repository(tmp_path / "app.sqlite")
    capture_id = repo.create_capture(
        original_name="demo.pcapng",
        stored_path=str(tmp_path / "demo.pcapng"),
        file_size=128,
        file_type="PCAPNG",
    )
    repo.save_ai_summary(capture_id, "Saved summary")
    app = create_app({"DATA_DIR": tmp_path, "TESTING": True})

    with app.test_client() as client:
        response = client.get(f"/api/captures/{capture_id}/ai/context")

    assert response.status_code == 200
    assert response.get_json()["saved_summary"]["summary"] == "Saved summary"
