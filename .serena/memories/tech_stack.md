# Tech Stack

- Frontend: Vue.
- Frontend-backend communication: HTTP RESTful APIs.
- Charts: ECharts.
- Streaming Markdown UI: markstream-vue.
- Backend: Python with Flask.
- PCAP/PCAPNG parsing: PyShark with `tshark`; runtime must have `tshark` installed.
- Logging/output: all command/runtime output goes through Loguru; Rich is only the rich-text formatting layer for Loguru output, not a direct output path.
- AI provider abstraction: LiteLLM, using DeepSeek for development testing.
- DeepSeek defaults: API base URL `https://api.deepseek.com`, model `deepseek-v4-pro`.
- Secrets: keep real API keys out of tracked files; use environment variables or local config.
- Persistence: SQLite for capture file paths, capture metadata, packet summaries, analysis status, and AI configuration metadata.
- Uploaded PCAP/PCAPNG files are stored on disk; SQLite stores their paths instead of file blobs.
- Upload size limit: 512 MB.
- Python environment/dependency management: uv with project-local dependencies.
- Runtime entry: root `main.py`; `uv run main.py backend` starts backend only, `uv run main.py frontend` starts frontend only.
- Project structure: backend under `src/backend`, frontend under `src/frontend`, runtime data under `data/`, samples/tests under `test/`.
- Current tracked content is Markdown/reference structure plus Serena/Superpowers metadata; app code has not been scaffolded yet.
- `markitdown` is available in the environment for document-to-Markdown conversion.