<script lang="ts">
  // Fusion Script Console UI: editor, server status, script storage.
  import {
    Button,
    Card,
    CheckBox,
    CodeView,
    Dialog, 
    Field,
    Hamburger,
    ThemeToggle,
    Tooltip,
    TEXT,
  } from "svelte-comp";
  import { Download, FileDown, Play, Trash2, Terminal, X } from "lucide-svelte";

  type Status = "idle" | "running" | "ok" | "error";
  type DialogAction = "save" | "delete" | null;
  type SavedScript = {
    name: string;
    code: string;
    updatedAt: number;
  };

  const defaultCode = `import adsk.core


def run(context):
    app = adsk.core.Application.get()
    app.log(app.activeDocument.name)
    return app.activeDocument.name
`;

  let serverUrl = $state("http://127.0.0.1:9100/mcp");
  let apiKey = $state("");
  let wrapInRun = $state(true);
  let code = $state(defaultCode);
  let output = $state("");
  let status = $state<Status>("idle");
  let lastError = $state("");
  let serverOnline = $state(false);
  let serverLastError = $state("");
  const scriptsStorageKey = "fusion-script-console.scripts";
  const legacyStorageKey = "fusion-script-console.code";
  const apiKeyStorageKey = "fusion-script-console.apiKey";

  const isRunning = $derived(status === "running");
  const statusLabel = $derived.by(() => {
    if (status === "running") return "Running";
    if (status === "ok") return "Ready";
    if (status === "error") return "Error";
    return "Idle";
  });
  const statusClass = $derived.by(() => {
    if (status === "running")
      return "bg-[var(--color-bg-warning)] text-[var(--color-text-warning)]";
    if (status === "ok")
      return "bg-[var(--color-bg-success)] text-[var(--color-text-success)]";
    if (status === "error")
      return "bg-[var(--color-bg-danger)] text-[var(--color-text-danger)]";
    return "bg-[var(--color-bg-muted)] text-[var(--color-text-muted)]";
  });
  let scripts = $state<SavedScript[]>([]);
  let active = $state("");
  let currentScriptName = $state("");
  let dialogOpen = $state(false);
  let dialogAction = $state<DialogAction>(null);
  let dialogName = $state("");
  let dialogError = $state("");
  let storageReady = $state(false);
  let authReady = $state(false);
  const menu = $derived(
    scripts.map((script) => ({ id: script.name, label: script.name }))
  );
  const dialogTitle = $derived.by(() =>
    dialogAction === "delete" ? "Delete script" : "Save script"
  );
  const dialogMessage = $derived.by(() =>
    dialogAction === "delete"
      ? "Delete the selected script from the list and clear the editor?"
      : "Save the current script to local storage under a name."
  );
  const serverStatusLabel = $derived.by(() =>
    serverOnline ? "Online" : "Offline"
  );
  const serverStatusClass = $derived.by(() =>
    serverOnline
      ? "bg-[var(--color-bg-success)] text-[var(--color-text-success)]"
      : "bg-[var(--color-bg-danger)] text-[var(--color-text-danger)]"
  );
  const appMeta = {
    version: "v0.0.1",
    title: "Fusion Script Console",
    footer: "(c) 2025 MaestroFusion360",
    authorUrl: "https://github.com/MaestroFusion360/FusionScriptConsole",
  };

  // Wrap raw code into run(context) when needed.
  function wrapCode(source: string): string {
    const lines = source.split("\n");
    return ["def run(context):", ...lines.map((line) => `    ${line}`)].join(
      "\n"
    );
  }

  // Convert MCP endpoint to /health URL.
  function getHealthUrl(url: string): string | null {
    try {
      const parsed = new URL(url);
      parsed.pathname = "/health";
      parsed.search = "";
      parsed.hash = "";
      return parsed.toString();
    } catch {
      return null;
    }
  }

  // Poll server health status.
  async function checkServerHealth(healthUrl: string) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200);
      const cacheBuster = healthUrl.includes("?") ? "&" : "?";
      const response = await fetch(`${healthUrl}${cacheBuster}t=${Date.now()}`, {
        method: "GET",
        cache: "no-store",
        headers: { "X-API-Key": apiKey },
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      if (response.ok) {
        serverOnline = true;
        serverLastError = "";
      } else {
        serverOnline = false;
        serverLastError = `HTTP ${response.status}`;
      }
    } catch (err) {
      serverOnline = false;
      serverLastError = err instanceof Error ? err.message : String(err);
    }
  }

  // Execute script via MCP.
  async function runScript() {
    status = "running";
    lastError = "";
    output = "Running...";

    let payload = code;
    if (wrapInRun && !/def\s+run\s*\(/.test(code)) {
      payload = wrapCode(code);
    }

    try {
      const response = await fetch(serverUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": apiKey,
        },
        body: JSON.stringify({ code: payload }),
      });

      const raw = await response.text();
      let data: any = null;
      try {
        data = JSON.parse(raw);
      } catch {
        status = response.ok ? "ok" : "error";
        output = `HTTP ${response.status}: ${raw || "(empty response)"}`;
        return;
      }

      const text =
        data?.output ??
        data?.result?.output ??
        data?.result?.content?.[0]?.text;
      if (text && String(text).trim().length) {
        output = String(text);
        status = "ok";
      } else if (data?.ok) {
        output = "OK (no output)";
        status = "ok";
      } else {
        output = JSON.stringify(data, null, 2);
        status = "error";
        lastError = data?.error ?? "Unknown error";
      }
    } catch (err) {
      status = "error";
      lastError = err instanceof Error ? err.message : String(err);
      output = `Request failed: ${lastError}`;
    }
  }

  async function copyOutput() {
    if (!output) return;
    try {
      await navigator.clipboard.writeText(output);
    } catch {
      lastError = "Clipboard write failed";
      status = "error";
    }
  }

  function clearOutput() {
    output = "";
    lastError = "";
    status = "idle";
  }

  // Save current script into local storage.
  function saveScript() {
    const name = dialogName.trim();
    if (!name) {
      dialogError = "Name is required.";
      dialogOpen = true;
      return;
    }
    const now = Date.now();
    const existing = scripts.find((script) => script.name === name);
    if (existing) {
      existing.code = code;
      existing.updatedAt = now;
      scripts = [...scripts];
    } else {
      scripts = [...scripts, { name, code, updatedAt: now }];
    }
    currentScriptName = name;
    active = name;
  }

  // Remove current script from storage and editor.
  function deleteScript() {
    if (currentScriptName) {
      scripts = scripts.filter((script) => script.name !== currentScriptName);
      currentScriptName = "";
      active = "";
    }
    code = "";
  }

  // Export all scripts into a single text file.
  function exportAllScripts() {
    if (!scripts.length) return;
    const parts = scripts.map((script) => `### ${script.name}\n${script.code}`);
    const content = parts.join("\n\n---\n\n");
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "fusion-scripts.txt";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function openDialog(action: DialogAction) {
    dialogAction = action;
    dialogError = "";
    dialogName = action === "save" ? currentScriptName : "";
    dialogOpen = true;
  }

  function handleDialogConfirm() {
    if (dialogAction === "save") {
      saveScript();
    } else if (dialogAction === "delete") {
      deleteScript();
    }
    if (!dialogError) {
      dialogOpen = false;
      dialogAction = null;
    }
  }

  function handleDialogClose() {
    dialogOpen = false;
    dialogAction = null;
    dialogError = "";
  }

  // Load a saved script from the menu.
  function handleMenuSelect(id: string) {
    active = id;
    const selected = scripts.find((script) => script.name === id);
    if (selected) {
      code = selected.code;
      currentScriptName = selected.name;
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      runScript();
    }
  }

  $effect(() => {
    if (storageReady) return;
    const saved = localStorage.getItem(scriptsStorageKey);
    if (saved) {
      try {
        scripts = JSON.parse(saved) ?? [];
      } catch {
        scripts = [];
      }
    } else {
      const legacy = localStorage.getItem(legacyStorageKey);
      if (legacy) {
        scripts = [{ name: "Untitled", code: legacy, updatedAt: Date.now() }];
        localStorage.removeItem(legacyStorageKey);
      }
    }
    storageReady = true;
  });

  $effect(() => {
    if (!storageReady) return;
    localStorage.setItem(scriptsStorageKey, JSON.stringify(scripts));
  });

  $effect(() => {
    if (authReady) return;
    const savedKey = localStorage.getItem(apiKeyStorageKey);
    if (savedKey) {
      apiKey = savedKey;
    }
    authReady = true;
  });

  $effect(() => {
    if (!authReady) return;
    localStorage.setItem(apiKeyStorageKey, apiKey);
  });

  $effect(() => {
    const healthUrl = getHealthUrl(serverUrl);
    if (!healthUrl) {
      serverOnline = false;
      serverLastError = "Invalid server URL";
      return;
    }
    let cancelled = false;
    const run = async () => {
      if (cancelled) return;
      await checkServerHealth(healthUrl);
    };
    run();
    const id = setInterval(run, 2000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  });
</script>

<svelte:window on:keydown={handleKeydown} />
<Dialog
  open={dialogOpen}
  title={dialogTitle}
  message={dialogMessage}
  onConfirm={handleDialogConfirm}
  onCancel={handleDialogClose}
  onClose={() => {}}
  class="fusion-dialog"
>
  <div class="mt-3 space-y-3">
    {#if dialogAction === "save"}
      <Field
        label="Script name"
        bind:value={dialogName}
        placeholder="My script"
      />
      {#if dialogError}
        <p class="text-xs text-[var(--color-text-danger)]">{dialogError}</p>
      {/if}
    {/if}
  </div>
</Dialog>

{#snippet editorHeader()}
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <p
        class="text-xs uppercase tracking-[0.18em] text-[var(--color-text-muted)]"
      >
        Fusion MCP
      </p>
      <h2 class="text-lg font-semibold">Fusion Script Console</h2>
    </div>
    <span
      class={`rounded-full px-3 py-1 text-xs font-semibold ${serverStatusClass}`}
    >
      {serverStatusLabel}
    </span>
  </div>
{/snippet}

{#snippet burgerHeader()}
  <div class="p-3 flex flex-col items-center text-center gap-1">
    <div class="text-sm font-semibold text-[var(--color-text-default)]">
      {appMeta.title}
    </div>
    <div
      class="text-[11px] uppercase tracking-[0.2em] text-[var(--color-text-muted)]"
    >
      {appMeta.version}
    </div>
  </div>
{/snippet}

{#snippet burgerFooter()}
  <div class="p-3 flex flex-col items-center text-center gap-3">
    <a
      class="text-xs italic text-[var(--color-text-muted)] hover:text-[var(--color-text-default)]"
      href={appMeta.authorUrl}
      target="_blank"
      rel="noreferrer"
    >
      {appMeta.footer}
    </a>
  </div>
{/snippet}

<main
  class="min-h-screen bg-[var(--color-bg-page)] text-[var(--color-text-default)]"
>
  <div class="flex items-center">
    <Hamburger
      header={burgerHeader}
      footer={burgerFooter}
      menuItems={menu}
      activeItem={active}
      onSelect={handleMenuSelect}
      closeOnSelect={true}
      width={300}
      class={TEXT.md}
    />
  </div>
  <div class="flex-1"></div>
  <Tooltip text="Toggle theme" position="left">
    <ThemeToggle class="fixed top-4 right-4 z-[200]" />
  </Tooltip>
  <div class="relative z-0 mx-auto flex max-w-5xl flex-col gap-6 px-6 py-10">
    <Card header={editorHeader} class="h-full">
      <div class="space-y-6">
        <div class="flex flex-wrap items-center gap-3">
          <div
            class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--color-bg-secondary)] text-[var(--color-text-default)] shadow-lg"
          >
            <Terminal class="h-5 w-5" />
          </div>
          <div>
            <p
              class="text-xs uppercase tracking-[0.35em] text-[var(--color-text-muted)]"
            >
              Fusion MCP
            </p>
            <p class="text-sm text-[var(--color-text-muted)]">
              Send Python to Fusion 360 and read the output.
            </p>
          </div>
        </div>

        <Field
          label="Server URL"
          type="url"
          bind:value={serverUrl}
          placeholder="http://127.0.0.1:9100/mcp"
        />
        <Field
          label="API Key"
          type="password"
          bind:value={apiKey}
          placeholder="Enter API key"
        />

        <div
          class="rounded-2xl border border-[var(--border-color-default)] bg-[var(--color-bg-surface)] shadow-sm shrink-0 overflow-hidden"
        >
          <div
            class="flex items-center justify-between border-b border-[var(--border-color-default)] bg-[var(--color-bg-muted)] px-4 py-2 text-[var(--color-text-default)]"
          >
            <p
              class="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]"
            >
              Python script
            </p>
            <span class="text-[11px] text-[var(--color-text-muted)]"
              >Ctrl+Enter to run</span
            >
          </div>

          <div class="editor-shell h-[320px] overflow-hidden">
            <CodeView
              bind:code
              language="python"
              title=""
              showCopyButton={true}
              showLineNumbers={true}
              editable={true}
              activeLine={true}
              sz="sm"
            />
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <CheckBox bind:checked={wrapInRun} label="Wrap in def run()" />
          <div class="flex items-center gap-2">
            <Tooltip text="Save script" position="top">
              <Button variant="secondary" onClick={() => openDialog("save")}>
                <Download class="h-4 w-4" />
              </Button>
            </Tooltip>
            <Tooltip text="Delete script" position="top">
              <Button variant="secondary" onClick={() => openDialog("delete")}>
                <Trash2 class="h-4 w-4" />
              </Button>
            </Tooltip>
            <Tooltip text="Export all scripts" position="top">
              <Button variant="secondary" onClick={exportAllScripts}>
                <FileDown class="h-4 w-4" />
              </Button>
            </Tooltip>
          </div>
          <div class="ml-auto flex items-center gap-2">
            <Tooltip text="Clear output" position="top">
              <Button variant="secondary" onClick={clearOutput}>
                <X class="h-4 w-4" />
              </Button>
            </Tooltip>
            <Tooltip text="Run script" position="top">
              <Button variant="primary" loaded={isRunning} onClick={runScript}>
                <Play class="h-4 w-4" />
              </Button>
            </Tooltip>
          </div>
        </div>

        <div
          class="rounded-2xl border border-[var(--border-color-default)] bg-[var(--color-bg-surface)] shadow-sm overflow-hidden"
        >
          <div
            class="flex items-center justify-between border-b border-[var(--border-color-default)] bg-[var(--color-bg-muted)] px-4 py-2 text-[var(--color-text-default)]"
          >
            <p
              class="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]"
            >
              Output
            </p>
            <span class="text-[11px] text-[var(--color-text-muted)]"
              >{output ? "" : "No output yet"}</span
            >
          </div>
          <div class="editor-shell h-[320px] overflow-hidden">
            <CodeView
              code={output || ""}
              language="txt"
              title=""
              showCopyButton={false}
              showLineNumbers={false}
              editable={false}
              sz="sm"
            />
          </div>
        </div>

        {#if lastError}
          <div
            class="rounded-lg border border-[var(--color-bg-danger)] bg-[var(--color-bg-danger)] px-3 py-2 text-xs text-[var(--color-text-danger)]"
          >
            {lastError}
          </div>
        {/if}
      </div>
    </Card>
  </div>
</main>
