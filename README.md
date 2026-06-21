# HZCU Network PCAP

Network Capture Analyzer is a local web app for uploading PCAP/PCAPNG files, parsing packets with `tshark`, viewing traffic statistics, and generating AI summaries.

## Features

- Upload and analyze `.pcap` and `.pcapng` files.
- Browse packets with filters for IPs, ports, protocol, and text search.
- View protocol distribution, traffic trends, top endpoints, and packet sizes.
- Generate AI summaries with saved results in SQLite.
- Keep AI API keys on the backend; keys are not returned to the frontend.

## Requirements

- Python 3.11+
- `uv`
- Node.js and `pnpm`
- `tshark`

On macOS, install `tshark` with:

```bash
brew install wireshark
```

## Setup

Install Python dependencies:

```bash
uv sync
```

Install frontend dependencies:

```bash
pnpm --dir src/frontend install
```

## Run

Start the backend:

```bash
UV_CACHE_DIR=.uv-cache uv run main.py backend
```

Start the frontend in another terminal:

```bash
pnpm --dir src/frontend dev --host 127.0.0.1
```

Open the frontend URL printed by Vite, usually:

```text
http://127.0.0.1:5173/
```

If port `5173` is busy, Vite prints another local URL.

## AI Summary

Open Settings in the app and configure:

- API base, for example `https://api.deepseek.com`
- Model name
- API key

The app stores settings locally in SQLite.

## Test

Run frontend tests:

```bash
pnpm test:frontend
```

Build the frontend:

```bash
pnpm build:frontend
```

Run backend tests:

```bash
UV_CACHE_DIR=.uv-cache uv run pytest test/backend/test_capture_flow.py
```

## License

MIT License. See [LICENSE](LICENSE).
