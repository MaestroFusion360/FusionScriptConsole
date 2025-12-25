<script lang="ts">
  import { getContext } from "svelte";
  import { TEXTS, type LangKey } from "../lang";

  type Props = {
    statusLabel?: string;
    statusClass?: string;
  };

  let { statusLabel = "", statusClass = "" }: Props = $props();

  const lang = getContext<{ value: LangKey }>("lang");
  const t = $derived(TEXTS[lang.value].app);
</script>

<div class="flex flex-wrap items-center justify-between gap-3">
  <div>
    <p class="text-xs uppercase tracking-[0.18em] text-[var(--color-text-muted)]">
      {t.brand}
    </p>
    <h2 class="text-lg font-semibold">{t.title}</h2>
  </div>
  <span class={`rounded-full px-3 py-1 text-xs font-semibold ${statusClass}`}>
    {statusLabel}
  </span>
</div>
