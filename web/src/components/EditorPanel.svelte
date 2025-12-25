<script lang="ts">
  import { getContext } from "svelte";
  import { Button, CheckBox, CodeView, Field, Tooltip } from "svelte-comp";
  import { Download, FileDown, Play, Trash2, Terminal, X } from "lucide-svelte";
  import { TEXTS, type LangKey } from "../lang";

  type Props = {
    serverUrl: string;
    apiKey: string;
    wrapInRun: boolean;
    autoImport: boolean;
    code: string;
    isRunning?: boolean;
    onOpenDialog?: (action: "save" | "delete") => void;
    onExportAll?: () => void;
    onClearOutput?: () => void;
    onRun?: () => void;
  };

  let {
    serverUrl = $bindable(),
    apiKey = $bindable(),
    wrapInRun = $bindable(),
    autoImport = $bindable(),
    code = $bindable(),
    isRunning = false,
    onOpenDialog = () => {},
    onExportAll = () => {},
    onClearOutput = () => {},
    onRun = () => {},
  }: Props = $props();

  const lang = getContext<{ value: LangKey }>("lang");
  const t = $derived(TEXTS[lang.value].app);
</script>

<div class="space-y-6">
  <div class="flex flex-wrap items-center gap-3">
    <div
      class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--color-bg-secondary)] text-[var(--color-text-default)] shadow-lg"
    >
      <Terminal class="h-5 w-5" />
    </div>
    <div>
      <p class="text-xs uppercase tracking-[0.35em] text-[var(--color-text-muted)]">
        {t.brand}
      </p>
      <p class="text-sm text-[var(--color-text-muted)]">{t.subtitle}</p>
    </div>
  </div>

  <Field
    label={t.fields.serverUrlLabel}
    type="url"
    bind:value={serverUrl}
    placeholder={t.fields.serverUrlPlaceholder}
  />
  <Field
    label={t.fields.apiKeyLabel}
    type="password"
    bind:value={apiKey}
    placeholder={t.fields.apiKeyPlaceholder}
  />

  <div
    class="rounded-2xl border border-[var(--border-color-default)] bg-[var(--color-bg-surface)] shadow-sm shrink-0 overflow-hidden"
  >
    <div
      class="flex items-center justify-between border-b border-[var(--border-color-default)] bg-[var(--color-bg-muted)] px-4 py-2 text-[var(--color-text-default)]"
    >
      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">
        {t.sections.pythonScript}
      </p>
      <span class="text-[11px] text-[var(--color-text-muted)]">
        {t.hints.runShortcut}
      </span>
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
    <CheckBox bind:checked={wrapInRun} label={t.checkbox.wrapInRun} />
    <CheckBox bind:checked={autoImport} label={t.checkbox.autoImport} />
    <div class="flex items-center gap-2">
      <Tooltip text={t.buttons.save} position="top">
        <Button variant="secondary" onClick={() => onOpenDialog("save")}>
          <Download class="h-4 w-4" />
        </Button>
      </Tooltip>
      <Tooltip text={t.buttons.delete} position="top">
        <Button variant="secondary" onClick={() => onOpenDialog("delete")}>
          <Trash2 class="h-4 w-4" />
        </Button>
      </Tooltip>
      <Tooltip text={t.buttons.exportAll} position="top">
        <Button variant="secondary" onClick={onExportAll}>
          <FileDown class="h-4 w-4" />
        </Button>
      </Tooltip>
    </div>
    <div class="ml-auto flex items-center gap-2">
      <Tooltip text={t.buttons.clearOutput} position="top">
        <Button variant="secondary" onClick={onClearOutput}>
          <X class="h-4 w-4" />
        </Button>
      </Tooltip>
      <Tooltip text={t.buttons.run} position="top">
        <Button variant="primary" loaded={isRunning} onClick={onRun}>
          <Play class="h-4 w-4" />
        </Button>
      </Tooltip>
    </div>
  </div>
</div>
