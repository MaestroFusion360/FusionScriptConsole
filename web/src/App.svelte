<script lang="ts">
  import { setContext } from "svelte";
  import { Card, ThemeToggle, Tooltip } from "svelte-comp";
  import { TEXTS, type LangKey } from "./lang";
  import HeaderStatus from "./components/HeaderStatus.svelte";
  import EditorPanel from "./components/EditorPanel.svelte";
  import OutputPanel from "./components/OutputPanel.svelte";
  import ScriptDialog, {
    type DialogAction,
  } from "./components/ScriptDialog.svelte";
  import SidebarMenu from "./components/SidebarMenu.svelte";
  import SearchOverlay from "./components/SearchOverlay.svelte";
  import type { SavedScript, Status } from "./lib/types";
  import {
    HEALTH_POLL_MS,
    buildPayload,
    checkServerHealth,
    getHealthUrl,
    getResultText,
    safeJsonParse,
  } from "./lib/api";
  import {
    loadApiKey,
    loadScripts,
    persistApiKey,
    persistScripts,
  } from "./lib/storage";
  import {
    buildExportContent,
    mergeImportedScripts,
    parseImportContent,
    removeScript,
    upsertScript,
  } from "./lib/scripts";

  const BASE_TEXTS = TEXTS.en;
  const DEFAULT_LANG: LangKey = "en";
  const DEFAULT_CODE = BASE_TEXTS.app.defaults.defaultCode;
  const DEFAULT_SERVER_URL = BASE_TEXTS.app.defaults.serverUrl;

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

  async function runScript() {
    status = "running";
    lastError = "";
    output = t.app.messages.running;

    const payload = buildPayload({
      source: code,
      wrapInRun,
      autoImport,
    });

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

    const next = upsertScript({
      scripts,
      name,
      code,
    });

    scripts = next.scripts;
    currentScriptName = next.activeName;
    active = next.activeName;
  }

  function deleteScript() {
    const next = removeScript({
      scripts,
      currentName: currentScriptName,
    });

    scripts = next.scripts;
    currentScriptName = next.currentName;
    active = next.activeName;
    code = "";
  }

  function exportAllScripts() {
    if (!scripts.length) return;

    const content = buildExportContent(scripts);
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

  async function importAllScripts() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".txt,text/plain";

    const file = await new Promise<File | null>((resolve) => {
      input.onchange = () => resolve(input.files?.[0] ?? null);
      input.click();
    });

    if (!file) return;

    try {
      const raw = await file.text();
      const imported = parseImportContent(raw);
      if (!imported.length) {
        lastError = t.app.messages.importInvalid;
        output = t.app.messages.importInvalid;
        status = "error";
        return;
      }

      scripts = mergeImportedScripts({ current: scripts, imported });
      output = `${t.app.messages.importSuccessPrefix}${imported.length}`;
      lastError = "";
      status = "ok";
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
      output = `${t.app.messages.importFailedPrefix}${lastError}`;
      status = "error";
    }
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

  $effect(() => {
    if (storageReady) return;
    scripts = loadScripts(t.app.defaults.legacyName);
    storageReady = true;
  });

  $effect(() => {
    if (!storageReady) return;
    persistScripts(scripts);
  });

  $effect(() => {
    if (authReady) return;
    apiKey = loadApiKey();
    authReady = true;
  });

  $effect(() => {
    if (!authReady) return;
    persistApiKey(apiKey);
  });

  $effect(() => {
    const healthUrl = getHealthUrl(serverUrl);
    if (!healthUrl) {
      serverOnline = false;
      lastError = t.app.messages.invalidServerUrl;
      return;
    }

    let cancelled = false;

    const run = async () => {
      if (cancelled) return;
      serverOnline = await checkServerHealth(healthUrl, apiKey);
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
  class="min-h-screen overflow-x-hidden bg-[var(--color-bg-page)] text-[var(--color-text-default)]"
>
  <div class="fixed left-3 top-3 z-[220] md:left-4 md:top-4">
    <SidebarMenu
      menu={menu}
      activeItem={active}
      onSelect={handleMenuSelect}
    />
  </div>
  <Tooltip text={t.app.buttons.toggleTheme} position="left">
    <ThemeToggle class="fixed right-3 top-3 z-[220] md:right-4 md:top-4" />
  </Tooltip>
  <div
    class="relative z-0 mx-auto flex w-full max-w-6xl flex-col gap-3 px-2 pb-8 pt-3 sm:px-4 md:gap-5 md:px-6 md:pb-10 md:pt-4"
  >
    <SearchOverlay
      bind:value={searchQuery}
      results={searchResults}
      onSelect={handleMenuSelect}
    />
    <div class="min-w-0">
      <Card header={editorHeader} class="h-full min-w-0">
        <div class="min-w-0 space-y-4 md:space-y-6">
        <EditorPanel
          bind:serverUrl
          bind:apiKey
          bind:wrapInRun
          bind:autoImport
          bind:code
          isRunning={isRunning}
          onOpenDialog={openDialog}
          onImportAll={importAllScripts}
          onExportAll={exportAllScripts}
          onClearOutput={clearOutput}
          onRun={runScript}
        />
        <OutputPanel {output} {lastError} />
        </div>
      </Card>
    </div>
  </div>
</main>
