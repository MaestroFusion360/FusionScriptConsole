# Fusion Script Console (Python + Svelte 5 Typescript + TailwindCSS)

Fusion 360 add-in with an API server and a Svelte interface for running Python scripts. Includes a start/stop panel, real-time status monitoring, and local script storage with names and export to a single file.

- API HTTP endpoints (`/api`, `/health`) for external tools
- Palette UI: editor, output, server status
- Scripts are stored in `localStorage` with names and export
- API access is protected by a token (API key)

---

<!-- markdownlint-disable MD033 -->
<details>
  <summary><h2>Table of Contents</h2></summary>

- [Fusion Script Console (Python + Svelte 5 Typescript + TailwindCSS)](#fusion-script-console-python--svelte-5-typescript--tailwindcss)
  - [Overview](#overview)
  - [Features](#features)
  - [UI](#ui)
  - [Token (API key)](#token-api-key)
  - [License](#license)

</details>

## Overview

The project combines a Python add-in for Fusion 360 with a Svelte 5 frontend. The add-in runs an API HTTP server and safely executes commands via TaskManager, while the UI lets you run and manage scripts directly from the palette.

This add-in is based on the Autodesk FusionMCPSample project:
[FusionMCPSample](https://github.com/AutodeskFusion360/FusionMCPSample)

License:
[FusionMCPSample LICENSE](https://github.com/AutodeskFusion360/FusionMCPSample/blob/main/LICENSE)

Source description:
Fusion MCP Add-in
A Fusion add-in that provides HTTP API functionality for Model Context Protocol (MCP) communication. MCP is a standardized protocol that enables AI assistants to interact with external tools and data sources. This add-in enables external applications (like Cursor) to interact with Fusion through a secure HTTP interface.

## Features

- API HTTP server with `/api` and `/health` endpoints
- Start/stop server buttons in a dedicated Fusion panel
- Real server status without extra animation
- Saved scripts menu with names, loading, and export

## UI

- Code editor, output view, run controls
- Save/delete via Dialog

## Token (API key)

The server listens only on `127.0.0.1`. The `/api` endpoint requires an API key, while `/health` is always available for status checks.
<!-- markdownlint-disable MD029 -->
1. Set the key in `.env`:

```txt
FUSION_API_SERVER_KEY=YOUR_KEY
```

2. Restart Fusion 360 (or the add-in).
3. Enter the same key in the UI field **API Key**.

Without a matching key the server returns `401 Unauthorized`.

## License

MIT License - See [LICENSE](LICENSE.md) for details.

---

<p align="center">
  <a href="https://github.com/MaestroFusion360/svelte-comp/issues">
    <img src="https://img.shields.io/github/issues/MaestroFusion360/FusionScriptConsole" alt="Issues" />
  </a>
  <a href="https://github.com/MaestroFusion360/FusionScriptConsole/stargazers">
    <img src="https://img.shields.io/github/stars/MaestroFusion360/FusionScriptConsole" alt="Stars" />
  </a>
</p>

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=MaestroFusion360-FusionScriptConsole&label=Project+Views&color=blue" alt="Project Views" />
</p>
