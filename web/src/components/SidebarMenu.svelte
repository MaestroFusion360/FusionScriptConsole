<script lang="ts">
  import { getContext } from "svelte";
  import { Hamburger, Select, TEXT } from "svelte-comp";
  import { TEXTS, type LangKey } from "../lang";

  type MenuItem = { id: string; label: string };

  type Props = {
    menu?: MenuItem[];
    activeItem?: string;
    onSelect?: (id: string) => void;
  };

  let { menu = [], activeItem = "", onSelect = () => {} }: Props = $props();

  const lang = getContext<{ value: LangKey }>("lang");
  const t = $derived(TEXTS[lang.value].app);
</script>

{#snippet burgerHeader()}
  <div class="p-3 flex flex-col items-center text-center gap-1">
    <div class="text-sm font-semibold text-[var(--color-text-default)]">
      {t.title}
    </div>
    <div class="text-[11px] uppercase tracking-[0.2em] text-[var(--color-text-muted)]">
      {t.version}
    </div>
  </div>
{/snippet}

{#snippet burgerFooter()}
  <div class="text-center p-2 flex flex-col items-center gap-4">
    <Select
      sz="sm"
      options={t.language.options}
      bind:value={lang.value}
      label={t.language.label}
    />
    <a
      class="text-xs italic text-[var(--color-text-muted)] hover:text-[var(--color-text-default)]"
      href={t.authorUrl}
      target="_blank"
      rel="noreferrer"
    >
      {t.footer}
    </a>
  </div>
{/snippet}

<Hamburger
  header={burgerHeader}
  footer={burgerFooter}
  menuItems={menu}
  activeItem={activeItem}
  onSelect={onSelect}
  closeOnSelect={true}
  width={300}
  class={TEXT.md}
/>
