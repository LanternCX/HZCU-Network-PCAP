---
version: alpha
name: Network Capture Analyzer
description: Frontend visual design system for a PCAP/PCAPNG analysis workspace.
reference:
  - https://vercel.com/design.md
  - docs/design/1.png
  - docs/design/2.png
  - docs/design/3.png
  - docs/design/4.png
  - docs/design/5.png
  - docs/design/6.png
colors:
  text-primary: "#0b1220"
  text-secondary: "#52617a"
  text-muted: "#7b879c"
  page: "#f7f9fc"
  surface: "#ffffff"
  surface-subtle: "#f9fafb"
  border: "#e5eaf2"
  border-strong: "#cfd8e6"
  blue-100: "#eef6ff"
  blue-700: "#006bff"
  blue-900: "#0047b3"
  teal-100: "#e8fbf7"
  teal-700: "#00a88f"
  teal-900: "#007768"
  amber-100: "#fff7e6"
  amber-700: "#f59e0b"
  amber-900: "#92400e"
  red-100: "#fff0f3"
  red-700: "#e11d48"
  red-900: "#9f1239"
  violet-100: "#f5f0ff"
  violet-700: "#7c3aed"
  violet-900: "#4c1d95"
typography:
  display:
    fontFamily: Geist Sans
    fontSize: 32px
    fontWeight: 600
    lineHeight: 40px
  title:
    fontFamily: Geist Sans
    fontSize: 20px
    fontWeight: 600
    lineHeight: 28px
  section:
    fontFamily: Geist Sans
    fontSize: 16px
    fontWeight: 600
    lineHeight: 24px
  body:
    fontFamily: Geist Sans
    fontSize: 14px
    fontWeight: 400
    lineHeight: 20px
  caption:
    fontFamily: Geist Sans
    fontSize: 12px
    fontWeight: 400
    lineHeight: 16px
  data:
    fontFamily: Geist Mono
    fontSize: 13px
    fontWeight: 400
    lineHeight: 18px
spacing:
  1: 4px
  2: 8px
  3: 12px
  4: 16px
  6: 24px
  8: 32px
  10: 40px
radius:
  control: 6px
  panel: 8px
  popover: 12px
  full: 9999px
shadow:
  panel: "0 2px 2px rgba(11, 18, 32, 0.04)"
  popover: "0 1px 1px rgba(11, 18, 32, 0.03), 0 12px 28px -16px rgba(11, 18, 32, 0.22)"
  drawer: "0 1px 1px rgba(11, 18, 32, 0.04), 0 20px 48px -24px rgba(11, 18, 32, 0.32)"
components:
  primary-button:
    backgroundColor: "{colors.blue-700}"
    textColor: "#ffffff"
    typography: "{typography.body}"
    rounded: "{radius.control}"
    height: 40px
    padding: "0 14px"
  secondary-button:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    borderColor: "{colors.border}"
    typography: "{typography.body}"
    rounded: "{radius.control}"
    height: 40px
    padding: "0 14px"
  danger-button:
    backgroundColor: "{colors.red-100}"
    textColor: "{colors.red-700}"
    borderColor: "#ffd6df"
    typography: "{typography.body}"
    rounded: "{radius.control}"
    height: 40px
    padding: "0 14px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    borderColor: "{colors.border}"
    typography: "{typography.body}"
    rounded: "{radius.control}"
    height: 40px
    padding: "0 12px"
---

# Network Capture Analyzer

## Overview

Network Capture Analyzer uses a precise light interface for reviewing packet captures. The mood is a network operations console: calm, technical, and data-dense. The UI should feel sharper than a generic admin dashboard while staying easy to scan during repeated analysis work.

Use the reference images in `docs/design/` for layout direction: left navigation, compact summary cards, bordered chart panels, dense tables, a right-side packet drawer, and a two-column AI analysis surface. Use Vercel Geist as the discipline model: neutral surfaces, restrained color, tight spacing, and explicit component states.

## Visual Principles

* Prefer white and near-white surfaces with thin borders over heavy shadows.
* Use color for meaning, not decoration.
* Use monospace text for packet numbers, IP addresses, ports, byte counts, timestamps, and protocol fields.
* Keep card radius at 8px or less. Controls use 6px.
* Keep pages dense but not cramped: 8px inside small groups, 16px between groups, 24px to 32px between sections.
* Avoid hero sections, decorative blobs, large gradients, marketing copy, and oversized empty cards.

## Color Intent

Blue is for navigation, links, focus rings, and primary actions. Teal is for completed, healthy, and streaming states. Amber is for warnings and suspicious traffic. Red is for failed states and destructive actions. Violet is reserved for AI features.

Status must always pair color with text or an icon. Do not rely on color alone.

## Typography

Use Geist Sans for UI and Geist Mono for data. If Geist is unavailable, choose close replacements with similar metrics. Do not mix more than two font families.

Use the token scale in the frontmatter. Most interface text should be 14px. Page titles use 32px. Table data uses 13px monospace where alignment matters.

## Layout

Desktop uses a fixed left sidebar around 232px wide and a fluid content area. Content pages use 24px padding and a maximum readable width when a page contains forms. Data-heavy pages may use the full content width.

Tablet collapses the sidebar and wraps cards to two columns. Mobile uses a top navigation bar, stacked cards, horizontally scrollable tables, and full-screen sheets for drawers.

## Surfaces

Page background is `page`. Main cards, tables, drawers, and forms use `surface`. Use `surface-subtle` only for gentle separation such as table headers, filter bars, or empty-state bands.

Panel borders use `border`. Active or selected areas use `border-strong` plus a subtle blue or teal background.

## Navigation

Sidebar items use icon plus text. Active navigation uses a pale blue/teal background, blue or teal icon, and semibold label. Hover states should be subtle and immediate.

Global navigation should stay compact:

```text
Dashboard
Captures
Settings
```

Packet and AI analysis views appear as capture detail tabs, not primary navigation pages. Statistics are shown through Dashboard charts and compact Overview charts.

## Cards

Summary cards use:

* 8px radius
* 1px border
* 24px padding on desktop
* Small icon tile on the left or right
* One primary number
* One short supporting line

Numbers must be prominent but not hero-sized. Use monospace only when alignment or technical reading matters.

## Tables

Tables are the core working surface. Use compact rows, clear headers, stable column widths, and horizontal scroll on small screens. Selected packet rows use a pale blue background and a stronger left or top border.

Recommended row states:

* Default: white
* Hover: `surface-subtle`
* Selected: blue-100
* Failed: red-100 accent with text status

## Drawers And Panels

Packet details open in a right-side drawer on desktop. The drawer uses `surface`, 8px radius on the exposed edge, `drawer` shadow, and stacked protocol sections.

On mobile, the drawer becomes a full-screen sheet with the same content order.

## Charts

Use ECharts with a consistent protocol palette:

* TCP: blue
* UDP: teal
* DNS: amber
* ICMP: orange/amber
* HTTP/HTTPS: light blue
* Other: gray

Charts must include nearby text summaries so the data is understandable without relying on color alone.

## AI Surfaces

AI areas use violet as the identifying accent, but streaming/healthy status still uses teal. The AI Analysis page should use a simple summary layout: selected capture panel, context preview panel, action bar, and Markdown summary panel.

AI content should look like a report inside the app: readable headings, short paragraphs, bullet lists, and visible analyzed-data context. Streaming text should not cause layout jumps. Do not design this as a general chat surface.

## Forms

Inputs are 40px high, 6px radius, white background, and border color `border`. Focus uses a two-layer ring: white gap plus `blue-700`.

Settings forms should be grouped into compact panels with clear section titles. Avoid nested cards.

Settings contains one AI Configuration panel only. Do not add general app, capture, or visualization settings panels.

## Motion

Use motion only to clarify state:

* Drawer: 220ms
* Popover/menu: 160ms
* Toast: 180ms
* Hover/focus: 0-120ms

Respect reduced-motion preferences.

## Content Voice

Use precise, action-first labels:

* `Upload Capture`
* `Retry Analysis`
* `Delete Capture`
* `Test Connection`
* `Summarize Capture`

Errors should say what happened and what to do next:

* `Analysis failed. Open details or retry analysis.`
* `No packets match these filters. Reset filters to view all packets.`
* `AI is not configured. Add API settings before starting analysis.`

## Accessibility

Every icon-only button needs a tooltip and accessible label. Focus rings must be visible. Drawers close with Escape and trap focus while open. Upload must support a normal file picker.
