import subprocess
import sys
from pathlib import Path

from loguru import logger
from rich.console import Console
from rich.logging import RichHandler


def configure_logging():
    logger.remove()
    logger.add(RichHandler(console=Console(), markup=True), format="{message}")


def run_backend():
    from src.backend.app import create_app

    app = create_app()
    logger.info("[bold blue]Backend[/bold blue] http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)


def run_frontend():
    frontend = Path(__file__).parent / "src" / "frontend"
    logger.info("[bold blue]Frontend[/bold blue] http://127.0.0.1:5173")
    subprocess.run(["pnpm", "dev", "--host", "127.0.0.1"], cwd=frontend, check=True)


def main():
    configure_logging()
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "backend":
        run_backend()
    elif command == "frontend":
        run_frontend()
    else:
        logger.error("Usage: uv run main.py backend|frontend")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
