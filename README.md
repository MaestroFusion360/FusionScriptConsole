# Fusion Script Console (Python + Svelte 5 Typescript + TailwindCSS)

Fusion 360 add-in with an MCP server and a Svelte interface for running Python scripts. Includes a built-in start/stop panel, real-time server status monitoring, and local script storage with named entries and export to a single file.

- MCP HTTP API (`/mcp`, `/health`) for external tools
- Palette UI: editor, output, server status
- Scripts are stored in `localStorage` with names and export

---
<!-- markdownlint-disable MD033 -->
<details>
  <summary><h2>Table of Contents</h2></summary>

- [Fusion Script Console (Python + Svelte 5 Typescript + TailwindCSS)](#fusion-script-console-python--svelte-5-typescript--tailwindcss)
  - [Overview](#overview)
  - [Features](#features)
  - [UI](#ui)
  - [📄 License](#-license)

</details>

## Overview

The project combines a Python add-in for Fusion 360 with a Svelte 5 frontend. The add-in runs an MCP HTTP server and safely executes commands via TaskManager, while the UI lets you run and manage scripts directly from the palette.

## Features

- MCP HTTP server with `/mcp` and `/health` endpoints
- Start/stop server buttons in a dedicated Fusion panel
- Real server status without extra animation
- Saved scripts menu with names, loading, and export

## UI

- Code editor, output view, run controls
- Save/delete via Dialog

## 📄 License

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
