<script lang="ts">
  import { setContext } from "svelte";
  import { Card, ThemeToggle, Tooltip } from "svelte-comp";
  import { TEXTS, type LangKey } from "./lang";
  import { SvelteURL } from "svelte/reactivity";
  import HeaderStatus from "./components/HeaderStatus.svelte";
  import EditorPanel from "./components/EditorPanel.svelte";
  import OutputPanel from "./components/OutputPanel.svelte";
  import ScriptDialog, {
    type DialogAction,
  } from "./components/ScriptDialog.svelte";
  import SidebarMenu from "./components/SidebarMenu.svelte";
  import SearchOverlay from "./components/SearchOverlay.svelte";

  type Status = "idle" | "running" | "ok" | "error";
  type SavedScript = {
    name: string;
    code: string;
    updatedAt: number;
  };
  type ApiResponse = {
    ok?: boolean;
    output?: unknown;
    error?: string;
    result?: {
      output?: unknown;
      content?: Array<{ text?: string }>;
    };
  };

  const BASE_TEXTS = TEXTS.en;
  const DEFAULT_LANG: LangKey = "en";
  const DEFAULT_CODE = BASE_TEXTS.app.defaults.defaultCode;
  const DEFAULT_SERVER_URL = BASE_TEXTS.app.defaults.serverUrl;
  const STORAGE_KEYS = {
    scripts: "fusion-script-console.scripts",
    legacy: "fusion-script-console.code",
    apiKey: "fusion-script-console.apiKey",
  };
  const HEALTH_POLL_MS = 2000;
  const HEALTH_TIMEOUT_MS = 1200;
  const RUN_DEF_RE = /def\s+run\s*\(/;
  const AUTO_IMPORT_LINES = [
    "import adsk.core",
    "import adsk.fusion",
    "import adsk.cam",
  ];
  const AUTO_IMPORT_RES = [
    /(^|\n)\s*import\s+adsk\.core\b/,
    /(^|\n)\s*import\s+adsk\.fusion\b/,
    /(^|\n)\s*import\s+adsk\.cam\b/,
  ];

  let langCtx = $state<{ value: LangKey }>({ value: DEFAULT_LANG });
  const t = $derived(TEXTS[langCtx.value]);
  setContext("lang", langCtx);

  let serverUrl = $state(DEFAULT_SERVER_URL);
  let apiKey = $state("");
  let wrapInRun = $state(true);
  let autoImport = $state(false);
  let code = $state(DEFAULT_CODE);
  let searchQuery = $state("");
  let output = $state("");
  let status = $state<Status>("idle");
  let lastError = $state("");
  let serverOnline = $state(false);

  const isRunning = $derived(status === "running");
  let scripts = $state<SavedScript[]>([]);
  let active = $state("");
  let currentScriptName = $state("");
  let dialogOpen = $state(false);
  let dialogAction = $state<DialogAction>(null);
  let dialogName = $state("");
  let dialogError = $state("");
  let storageReady = $state(false);
  let authReady = $state(false);
  const searchResults = $derived.by(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return [];
    return scripts.filter((script) => {
      const name = script.name.toLowerCase();
      const body = script.code.toLowerCase();
      return name.includes(query) || body.includes(query);
    });
  });
  const menu = $derived(
    scripts.map((script) => ({ id: script.name, label: script.name }))
  );
  const dialogTitle = $derived.by(() =>
    dialogAction === "delete"
      ? t.app.dialog.deleteTitle
      : t.app.dialog.saveTitle
  );
  const dialogMessage = $derived.by(() =>
    dialogAction === "delete"
      ? t.app.dialog.deleteMessage
      : t.app.dialog.saveMessage
  );
  const serverStatusLabel = $derived(
    serverOnline ? t.app.serverStatus.online : t.app.serverStatus.offline
  );
  const serverStatusClass = $derived(
    serverOnline
      ? "bg-[var(--color-bg-success)] text-[var(--color-text-success)]"
      : "bg-[var(--color-bg-danger)] text-[var(--color-text-danger)]"
  );


  function wrapCode(source: string): string {
    const lines = source.split("\n");
    return ["def run(context):", ...lines.map((line) => `    ${line}`)].join(
      "\n"
    );
  }

  function getHealthUrl(url: string): string | null {
    try {
      const parsed = new SvelteURL(url);
      parsed.pathname = "/health";
      parsed.search = "";
      parsed.hash = "";
      return parsed.toString();
    } catch {
      return null;
    }
  }

  function setServerStatus(isOnline: boolean) {
    serverOnline = isOnline;
  }

  async function checkServerHealth(healthUrl: string) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), HEALTH_TIMEOUT_MS);
      const cacheBuster = healthUrl.includes("?") ? "&" : "?";
      const response = await fetch(
        `${healthUrl}${cacheBuster}t=${Date.now()}`,
        {
          method: "GET",
          cache: "no-store",
          headers: { "X-API-Key": apiKey },
          signal: controller.signal,
        }
      );
      clearTimeout(timeoutId);
      if (response.ok) {
        setServerStatus(true);
      } else {
        setServerStatus(false);
      }
    } catch {
      setServerStatus(false);
    }
  }

  function safeJsonParse(
    raw: string
  ): { ok: true; data: ApiResponse } | { ok: false } {
    try {
      return { ok: true, data: JSON.parse(raw) as ApiResponse };
    } catch {
      return { ok: false };
    }
  }

  function normalizeText(value: unknown): string | null {
    if (value === null || value === undefined) {
      return null;
    }
    const text = String(value);
    return text.trim().length ? text : null;
  }

  function getResultText(data: ApiResponse): string | null {
    return (
      normalizeText(data.output) ??
      normalizeText(data.result?.output) ??
      normalizeText(data.result?.content?.[0]?.text) ??
      null
    );
  }

  function getPayload(): string {
    let header = "";
    if (autoImport) {
      const missing = AUTO_IMPORT_LINES.filter(
        (_, index) => !AUTO_IMPORT_RES[index].test(code)
      );
      if (missing.length) {
        header = `${missing.join("\n")}\n\n`;
      }
    }

    if (wrapInRun && !RUN_DEF_RE.test(code)) {
      return `${header}${wrapCode(code)}`;
    }
    return `${header}${code}`;
  }

  async function runScript() {
    status = "running";
    lastError = "";
    output = t.app.messages.running;

    const payload = getPayload();

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
      const parsed = safeJsonParse(raw);
      if (!parsed.ok) {
        status = response.ok ? "ok" : "error";
        output = `${t.app.messages.httpPrefix} ${response.status}: ${
          raw || t.app.messages.emptyResponse
        }`;
        return;
      }

      const text = getResultText(parsed.data);
      if (text && String(text).trim().length > 0) {
        output = String(text);
        status = "ok";
      } else if (parsed.data?.ok) {
        output = t.app.messages.okNoOutput;
        status = "ok";
      } else {
        output = JSON.stringify(parsed.data, null, 2);
        status = "error";
        lastError = parsed.data?.error ?? t.app.messages.unknownError;
      }
    } catch (err) {
      status = "error";
      lastError = err instanceof Error ? err.message : String(err);
      output = `${t.app.messages.requestFailedPrefix}${lastError}`;
    }
  }

  function clearOutput() {
    output = "";
    lastError = "";
    status = "idle";
  }

  function saveScript() {
    const name = dialogName.trim();
    if (!name) {
      dialogError = t.app.dialog.nameRequired;
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

  function exportAllScripts() {
    if (!scripts.length) return;
    const parts = scripts.map(
      (script) => `"""${script.name}"""\n${script.code}`
    );
    const content = parts.join("\n\n---\n\n");
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = t.app.defaults.exportFileName;
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

  function loadScripts(): SavedScript[] {
    const saved = localStorage.getItem(STORAGE_KEYS.scripts);
    if (saved) {
      try {
        return JSON.parse(saved) ?? [];
      } catch {
        return [];
      }
    }
    const legacy = localStorage.getItem(STORAGE_KEYS.legacy);
    if (legacy) {
      localStorage.removeItem(STORAGE_KEYS.legacy);
      return [
        {
          name: t.app.defaults.legacyName,
          code: legacy,
          updatedAt: Date.now(),
        },
      ];
    }
    return [];
  }

  function persistScripts() {
    localStorage.setItem(STORAGE_KEYS.scripts, JSON.stringify(scripts));
  }

  function loadApiKey(): string {
    return localStorage.getItem(STORAGE_KEYS.apiKey) ?? "";
  }

  function persistApiKey() {
    localStorage.setItem(STORAGE_KEYS.apiKey, apiKey);
  }

  $effect(() => {
    if (storageReady) return;
    scripts = loadScripts();
    storageReady = true;
  });

  $effect(() => {
    if (!storageReady) return;
    persistScripts();
  });

  $effect(() => {
    if (authReady) return;
    apiKey = loadApiKey();
    authReady = true;
  });

  $effect(() => {
    if (!authReady) return;
    persistApiKey();
  });

  $effect(() => {
    const healthUrl = getHealthUrl(serverUrl);
    if (!healthUrl) {
      setServerStatus(false);
      lastError = t.app.messages.invalidServerUrl;
      return;
    }
    let cancelled = false;
    const run = async () => {
      if (cancelled) return;
      await checkServerHealth(healthUrl);
    };
    run();
    const id = setInterval(run, HEALTH_POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  });
</script>

<svelte:window on:keydown={handleKeydown} />
<ScriptDialog
  open={dialogOpen}
  title={dialogTitle}
  message={dialogMessage}
  action={dialogAction}
  bind:name={dialogName}
  error={dialogError}
  onConfirm={handleDialogConfirm}
  onCancel={handleDialogClose}
  onClose={() => {}}
/>

{#snippet editorHeader()}
  <HeaderStatus statusLabel={serverStatusLabel} statusClass={serverStatusClass} />
{/snippet}

<main
  class="min-h-screen bg-[var(--color-bg-page)] text-[var(--color-text-default)]"
>
  <div class="flex items-center">
    <SidebarMenu
      menu={menu}
      activeItem={active}
      onSelect={handleMenuSelect}
    />
  </div>
  <div class="flex-1"></div>
  <Tooltip text={t.app.buttons.toggleTheme} position="left">
    <ThemeToggle class="fixed top-4 right-4 z-[200]" />
  </Tooltip>
  <SearchOverlay
    bind:value={searchQuery}
    results={searchResults}
    onSelect={handleMenuSelect}
  />
  <div class="relative z-0 mx-auto flex max-w-5xl flex-col gap-6 px-6 py-10 pt-24">
    <Card header={editorHeader} class="h-full">
      <div class="space-y-6">
        <EditorPanel
          bind:serverUrl
          bind:apiKey
          bind:wrapInRun
          bind:autoImport
          bind:code
          isRunning={isRunning}
          onOpenDialog={openDialog}
          onExportAll={exportAllScripts}
          onClearOutput={clearOutput}
          onRun={runScript}
        />
        <OutputPanel {output} {lastError} />
      </div>
    </Card>
  </div>
</main>




