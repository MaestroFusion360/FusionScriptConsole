<script lang="ts">
  import {
    Button,
    Card,
    CheckBox,
    CodeView,
    Dialog,
    Field,
    Hamburger,
    Select,
    ThemeToggle,
    Tooltip,
    TEXT,
  } from "svelte-comp";
  import { Download, FileDown, Play, Trash2, Terminal, X } from "lucide-svelte";
  import { TEXTS, type LangKey } from "./lang";
  import { SvelteURL } from "svelte/reactivity";

  type Status = "idle" | "running" | "ok" | "error";
  type DialogAction = "save" | "delete" | null;
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

  let langCtx = $state<{ value: LangKey }>({ value: DEFAULT_LANG });
  const t = $derived(TEXTS[langCtx.value]);

  let serverUrl = $state(DEFAULT_SERVER_URL);
  let apiKey = $state("");
  let wrapInRun = $state(true);
  let code = $state(DEFAULT_CODE);
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


  const appMeta = $derived({
    version: t.app.version,
    title: t.app.title,
    footer: t.app.footer,
    authorUrl: t.app.authorUrl,
  });

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
    if (wrapInRun && !RUN_DEF_RE.test(code)) {
      return wrapCode(code);
    }
    return code;
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
    const parts = scripts.map((script) => `### ${script.name}\n${script.code}`);
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
        label={t.app.fields.scriptNameLabel}
        bind:value={dialogName}
        placeholder={t.app.fields.scriptNamePlaceholder}
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
        {t.app.brand}
      </p>
      <h2 class="text-lg font-semibold">{t.app.title}</h2>
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
  <div class="text-center p-2 flex flex-col items-center gap-4">
    <Select
      sz="sm"
      options={t.app.language.options}
      bind:value={langCtx.value}
      label={t.app.language.label}
    />
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
  <Tooltip text={t.app.buttons.toggleTheme} position="left">
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
              {t.app.brand}
            </p>
            <p class="text-sm text-[var(--color-text-muted)]">
              {t.app.subtitle}
            </p>
          </div>
        </div>

        <Field
          label={t.app.fields.serverUrlLabel}
          type="url"
          bind:value={serverUrl}
          placeholder={t.app.fields.serverUrlPlaceholder}
        />
        <Field
          label={t.app.fields.apiKeyLabel}
          type="password"
          bind:value={apiKey}
          placeholder={t.app.fields.apiKeyPlaceholder}
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
              {t.app.sections.pythonScript}
            </p>
            <span class="text-[11px] text-[var(--color-text-muted)]"
              >{t.app.hints.runShortcut}</span
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
          <CheckBox bind:checked={wrapInRun} label={t.app.checkbox.wrapInRun} />
          <div class="flex items-center gap-2">
            <Tooltip text={t.app.buttons.save} position="top">
              <Button variant="secondary" onClick={() => openDialog("save")}>
                <Download class="h-4 w-4" />
              </Button>
            </Tooltip>
            <Tooltip text={t.app.buttons.delete} position="top">
              <Button variant="secondary" onClick={() => openDialog("delete")}>
                <Trash2 class="h-4 w-4" />
              </Button>
            </Tooltip>
            <Tooltip text={t.app.buttons.exportAll} position="top">
              <Button variant="secondary" onClick={exportAllScripts}>
                <FileDown class="h-4 w-4" />
              </Button>
            </Tooltip>
          </div>
          <div class="ml-auto flex items-center gap-2">
            <Tooltip text={t.app.buttons.clearOutput} position="top">
              <Button variant="secondary" onClick={clearOutput}>
                <X class="h-4 w-4" />
              </Button>
            </Tooltip>
            <Tooltip text={t.app.buttons.run} position="top">
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
              {t.app.sections.output}
            </p>
            <span class="text-[11px] text-[var(--color-text-muted)]"
              >{output ? "" : t.app.hints.noOutput}</span
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




