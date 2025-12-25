<script lang="ts">
  import { getContext } from "svelte";
  import { SearchInput } from "svelte-comp";
  import { TEXTS, type LangKey } from "../lang";

  type ScriptItem = { name: string; code: string };
  type Props = {
    value?: string;
    results?: ScriptItem[];
    onSelect?: (name: string) => void;
  };

  let {
    value = $bindable(""),
    results = [],
    onSelect = () => {},
  }: Props = $props();

  const lang = getContext<{ value: LangKey }>("lang");
  const t = $derived(TEXTS[lang.value].app);
  const showResults = $derived(value.trim().length > 0);

  function getPreview(code: string) {
    const line = code.split("\n").find((item) => item.trim().length);
    return line ?? "";
  }
</script>

<div class="fixed top-4 left-1/2 z-[300] w-[min(520px,calc(100%-3rem))] -translate-x-1/2 pointer-events-auto">
  <SearchInput
    bind:value
    label={t.fields.searchLabel}
    placeholder={t.fields.searchPlaceholder}
    class="w-full"
  />
  {#if showResults}
    <div class="relative">
      <div
        class="absolute left-0 right-0 mt-2 z-[210] max-h-[280px] overflow-auto border border-[var(--border-color-default)] bg-[var(--color-bg-surface)] shadow-xl pointer-events-auto"
      >
        {#if results.length === 0}
          <div class="px-4 py-2 text-xs text-[var(--color-text-muted)]">
            {t.messages.searchNoResults}
          </div>
        {:else}
          {#each results as script (script.name)}
            <button
              type="button"
              class="w-full text-left px-4 py-2 transition-colors hover:bg-[var(--color-bg-hover)]"
              onclick={() => {
                onSelect(script.name);
                value = "";
              }}
            >
              <div class="text-sm font-semibold text-[var(--color-text-default)]">
                {script.name}
              </div>
              <div class="text-[11px] text-[var(--color-text-muted)] truncate">
                {getPreview(script.code)}
              </div>
            </button>
          {/each}
        {/if}
      </div>
    </div>
  {/if}
</div>
