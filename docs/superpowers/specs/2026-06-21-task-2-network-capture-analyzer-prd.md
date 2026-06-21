# Status: Active

# Task 2 Network Capture Analyzer PRD

## 1. Product Goal

Network Capture Analyzer is a browser-based workspace for uploading PCAP/PCAPNG files, reviewing packet-level details, and visualizing traffic behavior.

The first version includes all required assignment features and one extra-credit feature:

* Capture upload, storage, download, deletion, retry, and status tracking
* Capture overview and key indicators
* Packet table with filtering, sorting, pagination, and packet details
* Protocol distribution and traffic trend charts
* Dashboard statistics for protocol distribution, traffic trend, endpoints, ports, and packet sizes
* Settings for AI configuration
* Extra-credit AI Analysis worth 10 points, focused on capture summaries, anomalies, traffic spikes, and selected-packet explanation

## 2. Product Scope

### In Scope

* Upload PCAP and PCAPNG files up to 512 MB.
* Store uploaded files on disk, and store file paths plus metadata in SQLite.
* Analyze uploaded captures after upload.
* Track capture status: Uploaded, Analyzing, Completed, Failed.
* List captures with search, status filter, and file actions.
* Show capture overview, packets, and extra-credit AI analysis tabs.
* Render charts with ECharts.
* Render streamed AI Markdown with `markstream-vue`.
* Configure AI connection settings.

### Out Of Scope

* Multi-user permissions.
* Real-time live packet capture.
* Team collaboration.
* Cloud billing or deployment management.

## 3. Tech Stack

Frontend:

* Vue for the web application.
* ECharts for protocol, trend, endpoint, port, and packet-size charts.
* markstream-vue for streamed Markdown rendering in AI Analysis.

Backend:

* Python for backend implementation.
* Flask for HTTP APIs, file upload/download, analysis endpoints, and AI streaming endpoints.
* PyShark with `tshark` for PCAP/PCAPNG parsing and protocol detail extraction.
* SQLite for local persistence of capture file paths, capture metadata, packet summaries, analysis status, and AI configuration metadata.
* LiteLLM for connecting the AI Analysis feature to DeepSeek or another compatible model provider.
* DeepSeek API defaults:
  * API base URL: `https://api.deepseek.com`
  * Default model: `deepseek-v4-pro`
* Loguru for backend logging and command output.
* Rich only as the rich-text formatting layer for Loguru output.
* uv for project-local Python dependency and environment management.
* HTTP RESTful APIs for frontend-backend communication.

Runtime entry:

* Root `main.py` is the project entry point.
* `uv run main.py backend` starts the Flask backend only.
* `uv run main.py frontend` starts the Vue frontend only.
* `main.py` should keep frontend and backend startup separate instead of hiding both behind one command.
* `main.py` should send command output through Loguru; do not print directly with Rich.
* Loguru output should be rendered as rich text for readable local status messages.

## 4. Navigation

Global navigation:

```text
Dashboard
Captures
Settings
```

Packet and AI analysis views belong to a selected capture. They are not global first-version pages.

## 5. Routes

```text
/                         Dashboard
/captures                 Capture list
/captures/:id             Capture detail
/settings                 Settings
```

Capture detail uses query-based tabs:

```text
/captures/:id?tab=overview
/captures/:id?tab=packets
/captures/:id?tab=ai
```

## 6. UI Structure And Interaction Pattern

Use a clear master-detail pattern:

* Dashboard is for system-wide reading and quick entry.
* Captures is for file management.
* Capture Detail is for working on one selected capture.
* Settings is for AI connection setup only.

Use tabs only inside Capture Detail, because tabs switch between different ways to inspect the same capture:

```text
Overview
Packets
AI Analysis
```

Use panels inside each page for grouped content:

* Summary panel: key metrics and short status signals.
* Chart panel: protocol, trend, endpoint, port, or packet-size visualization.
* Table panel: searchable and actionable rows.
* Detail drawer: packet-level protocol inspection without leaving the packet table.
* AI panel: selected capture summary action and streamed summary output.

Use progressive disclosure:

* Dashboard shows trends and hotspots, not packet rows.
* Captures shows file rows and actions, not analysis charts.
* Overview shows a selected capture summary, not packet-level protocol fields.
* Packets shows packet rows first; protocol details appear only after row selection.
* AI Analysis shows the selected capture and one summarize action first; transmitted context details appear only when the user starts the summary.

Primary actions should stay obvious:

* Dashboard: `Upload Capture`
* Captures: `Open`, `Download`, `Retry Analysis`, `Delete`
* Packets: select a packet row to inspect details
* AI Analysis: summarize the selected capture
* Settings: `Test Connection`

## 7. Dashboard

The dashboard is the system-wide overview for all uploaded captures.

Required content:

* Upload Capture button
* Summary cards:
  * Total Captures
  * Total Packets
  * Total Size
  * Completed
  * Failed/Alerts
* Recent Captures table/list
* System-wide Protocol Distribution chart
* System-wide Traffic Trend chart
* Top Source IPs
* Top Destination IPs
* Top Destination Ports
* Packet Size Distribution

Chart controls:

* Metric: Packets / Bytes
* Interval: 1 second / 10 seconds / 1 minute
* Optional protocol filter

Primary action:

* `Upload Capture`

Empty state:

* `No captures yet. Upload a PCAP or PCAPNG file to start analysis.`

## 8. Captures Page

The Captures page manages uploaded files. It does not repeat dashboard summary cards.

Top controls:

* Search by filename
* Filter by status
* Upload Capture button

Table columns:

| Column | Content |
| --- | --- |
| File Name | Original filename with file icon |
| Type | PCAP or PCAPNG |
| Packets | Extracted packet count |
| Size | File size |
| Duration | Capture start to end duration |
| Uploaded At | Upload time |
| Status | Uploaded, Analyzing, Completed, Failed |
| Actions | Open, Download, Reanalyze, Delete |

Actions:

* Open capture detail
* Download original file
* Retry failed analysis
* Delete capture with confirmation

Failed rows expose a short error message in a tooltip or row expansion.

## 9. Capture Detail Layout

Header:

* Back to Captures link
* Filename
* Status label
* Metadata row:
  * Packet count
  * File size
  * Duration
  * Uploaded time
* Download button
* Delete button

Tabs:

```text
Overview
Packets
AI Analysis
```

Tabs stay within the detail page and should not reload the whole layout.

## 10. Overview Tab

The Overview tab answers: “What is inside this selected capture?” It shows per-capture summary only.

Summary cards:

* Total Packets
* Capture Duration
* Average Packets Per Second
* Total Traffic Size
* Source IP Count
* Destination IP Count

Sections:

* Basic Information:
  * Original filename
  * File type
  * File size
  * Capture start time
  * Capture end time
  * Analysis time
* Top Source IPs
* Top Destination IPs
* Top Protocols
* Top Destination Ports
* Compact Protocol Distribution chart
* Compact Traffic Trend chart

## 11. Packets Tab

The Packets tab is the main explorer.

Filter bar:

* Search IP, port, or protocol
* Protocol select
* Source IP input
* Destination IP input
* Port input
* Reset button

Table columns:

| Column | Content |
| --- | --- |
| No. | Packet number |
| Timestamp | Capture timestamp |
| Source IP | Source address |
| Source Port | Source port |
| Destination IP | Destination address |
| Destination Port | Destination port |
| Protocol | Protocol label |
| Length | Packet length |

Required behavior:

* Server-side pagination
* Page-size selection
* Sort by timestamp and length
* Loading state
* Empty filtered state
* Error state with retry

Packet details:

* Open a right-side drawer when a row is selected.
* Keep the table visible behind the drawer.
* Show protocol sections in order:
  * Frame
  * Ethernet
  * IPv4/IPv6
  * TCP/UDP/ICMP
  * DNS/HTTP when available
  * Raw summary when a protocol is unsupported

## 12. AI Analysis Tab

The AI Analysis tab is included in version 1 as the extra-credit feature worth 10 points. It produces one AI summary for the selected capture.

Layout:

* Selected capture panel:
  * Current filename
  * Packet count
  * Capture duration
  * Analysis status
* Context preview panel:
  * Protocol distribution summary
  * Traffic trend summary
  * Top source IPs
  * Top destination IPs
  * Top destination ports
  * Small representative packet sample
* Action bar:
  * Summarize Capture button
  * Stop button while streaming
  * Regenerate Summary button after a response
  * Copy Summary button
* Summary panel:
  * Streaming Markdown output
  * Empty state before first summary

Use `markstream-vue` for streamed Markdown rendering.

Prompt safety:

* Do not send the raw PCAP/PCAPNG file to the model.
* Do not send every packet to the model.
* Send only analyzed data: statistics, top endpoints, traffic trend summary, protocol counts, and a small representative packet sample.
* Show the context preview before sending, so the user knows what the AI will summarize.

AI states:

* Not configured
* Ready
* Streaming
* Failed
* Stopped

## 13. Settings Page

The Settings page only configures the extra-credit AI feature.

* API base URL
* API key input
* Model name
* Streaming responses toggle
* Test connection button

API keys should be handled by the backend or environment configuration. Do not store API keys in browser local storage.

## 14. Project And Component Structure

```text
main.py
pyproject.toml
uv.lock
src/
├── backend/
│   ├── app.py
│   ├── api/
│   │   ├── captures.py
│   │   ├── packets.py
│   │   ├── statistics.py
│   │   ├── ai.py
│   │   └── settings.py
│   ├── services/
│   │   ├── capture_analyzer.py
│   │   ├── file_storage.py
│   │   └── ai_summary.py
│   └── db/
│       ├── schema.py
│       └── repository.py
├── frontend/
│   ├── src/
│   │   ├── layouts/
│   │   │   └── AppLayout.vue
│   │   ├── views/
│   │   │   ├── DashboardView.vue
│   │   │   ├── CapturesView.vue
│   │   │   ├── CaptureDetailView.vue
│   │   │   └── SettingsView.vue
│   │   ├── components/
│   │   │   ├── captures/
│   │   │   ├── packets/
│   │   │   ├── charts/
│   │   │   └── ai/
│   │   ├── api/
│   │   └── stores/
│   └── package.json
data/
├── captures/
└── app.sqlite
test/
├── demo.pcapng
├── backend/
└── frontend/
```

Structure rules:

* Keep backend code under `src/backend`.
* Keep frontend code under `src/frontend`.
* Keep runtime upload storage under `data/captures`.
* Keep SQLite database at `data/app.sqlite`.
* Keep sample files and tests under `test`.
* Keep generated runtime files out of Git.

## 15. State And Data Flow

Capture flow:

```text
Frontend uploads file through HTTP RESTful API -> Backend stores file on disk -> Backend stores file path in SQLite -> Backend analyzes packets -> Frontend polls HTTP RESTful API for status -> Detail pages read analyzed data through HTTP RESTful API
```

Parsing requirement:

* Backend analysis uses PyShark, which requires `tshark` to be installed on the runtime machine.
* If `tshark` is missing, uploaded captures should move to Failed status with a clear setup message.
* Local development can use `test/demo.pcapng` as a sample capture file.

Packet flow:

```text
User filters table -> Frontend sends HTTP query params -> Backend returns one page -> User selects packet -> Drawer fetches full packet detail through HTTP RESTful API
```

Dashboard statistics flow:

```text
Capture completed -> Backend prepares statistics -> Dashboard and Overview render charts from aggregated data
```

AI flow:

```text
User opens AI Analysis for a selected capture -> Frontend requests analyzed-data context preview through HTTP RESTful API -> User clicks Summarize Capture -> Backend sends analyzed data to LiteLLM without raw file content -> Backend streams Markdown over HTTP -> Frontend renders summary
```

AI configuration:

* Use LiteLLM-compatible model names.
* Use DeepSeek for development testing.
* Default DeepSeek model is `deepseek-v4-pro`.
* Default DeepSeek API base URL is `https://api.deepseek.com`.
* Store API keys outside tracked files, such as an environment variable. Do not write real API keys into Git.

## 16. Error And Empty States

Upload errors:

* Unsupported file type
* File too large, with 512 MB as the maximum upload size
* Upload failed
* Analysis failed

Table states:

* Loading skeleton
* Empty capture list
* Empty filtered result
* Failed request with retry

AI states:

* AI not configured
* Connection test failed
* Stream interrupted
* Empty conversation

Use direct messages:

* `Analysis failed. Open details or retry analysis.`
* `No packets match these filters. Reset filters to view all packets.`
* `AI is not configured. Add API settings before starting analysis.`

## 17. Accessibility

* Every icon-only button needs a tooltip and accessible label.
* Focus rings must be visible on keyboard navigation.
* Status must not rely on color alone.
* Tables need clear headers.
* Drawer must trap focus while open and close with Escape.
* Chart data must have text summaries near each chart.
* Upload must use a standard file picker button.

## 18. Responsive Behavior

Desktop:

* Persistent sidebar
* Multi-column cards and charts
* Packet drawer opens from the right

Tablet:

* Sidebar collapses
* Cards wrap to two columns
* Charts stack when needed

Mobile:

* Top navigation menu
* Cards stack vertically
* Tables become horizontally scrollable
* Packet detail drawer becomes a full-screen sheet

## 19. Development Priority

1. App shell, routing, sidebar, and design tokens
2. Capture upload and capture list
3. Capture detail header and Overview tab
4. Packet table, filters, pagination, and packet drawer
5. Dashboard and Overview charts
6. File download, deletion, retry, and status handling
7. Extra-credit AI Analysis tab with streaming Markdown
8. Settings page
9. Responsive polish, empty states, and accessibility checks

## 20. Review Checklist

* Version 1 includes AI Analysis as the 10-point extra-credit feature.
* Detail tabs are inside `/captures/:id`.
* Global navigation stays limited to Dashboard, Captures, and Settings.
* Visual style follows `design.md`.
* API keys are not stored in browser local storage.
* The app remains useful when there are no captures, failed captures, or no AI configuration.
