from pathlib import Path

from flask import Flask

from src.backend.api.ai import bp as ai_bp
from src.backend.api.captures import bp as captures_bp
from src.backend.api.packets import bp as packets_bp
from src.backend.api.settings import bp as settings_bp
from src.backend.api.statistics import bp as statistics_bp
from src.backend.db.repository import Repository


def create_app(config=None):
    app = Flask(__name__)
    root = Path(__file__).resolve().parents[2]
    app.config.update(DATA_DIR=root / "data", MAX_CONTENT_LENGTH=512 * 1024 * 1024)
    if config:
        app.config.update(config)
    data_dir = Path(app.config["DATA_DIR"])
    app.config["REPOSITORY"] = Repository(data_dir / "app.sqlite")
    app.register_blueprint(captures_bp)
    app.register_blueprint(packets_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(settings_bp)

    @app.get("/api/health")
    def health():
        return {"ok": True}

    return app
