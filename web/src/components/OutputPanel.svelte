<script lang="ts">
  import { getContext } from "svelte";
  import { CodeView } from "svelte-comp";
  import { TEXTS, type LangKey } from "../lang";

  type Props = {
    output?: string;
    lastError?: string;
  };

  let { output = "", lastError = "" }: Props = $props();

  const lang = getContext<{ value: LangKey }>("lang");
  const t = $derived(TEXTS[lang.value].app);
</script>

<div
  class="min-w-0 overflow-hidden rounded-2xl border border-[var(--border-color-default)] bg-[var(--color-bg-surface)] shadow-sm"
>
  <div
    class="flex items-center justify-between border-b border-[var(--border-color-default)] bg-[var(--color-bg-muted)] px-4 py-2 text-[var(--color-text-default)]"
  >
    <p class="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">
      {t.sections.output}
    </p>
    <span class="text-[11px] text-[var(--color-text-muted)]">
      {output ? "" : t.hints.noOutput}
    </span>
  </div>
  <div class="editor-shell h-56 overflow-hidden md:h-[320px]">
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
    class="break-words rounded-lg border border-[var(--color-bg-danger)] bg-[var(--color-bg-danger)] px-3 py-2 text-xs text-[var(--color-text-danger)]"
  >
    {lastError}
  </div>
{/if}
