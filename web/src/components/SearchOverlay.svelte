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

<div class="relative z-[120] mx-auto mt-4 w-full max-w-[520px] pointer-events-auto md:mt-5">
  <SearchInput
    bind:value
    placeholder={t.fields.searchPlaceholder}
    class="w-full"
  />
  {#if showResults}
    <div class="relative">
      <div
        class="absolute left-0 right-0 z-[210] mt-2 max-h-[45vh] overflow-auto border border-[var(--border-color-default)] bg-[var(--color-bg-surface)] shadow-xl pointer-events-auto md:max-h-[280px]"
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
