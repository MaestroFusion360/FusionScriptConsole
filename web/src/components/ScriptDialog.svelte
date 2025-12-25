<script lang="ts">
  import { getContext } from "svelte";
  import { Dialog, Field } from "svelte-comp";
  import { TEXTS, type LangKey } from "../lang";

  export type DialogAction = "save" | "delete" | null;

  type Props = {
    open?: boolean;
    title?: string;
    message?: string;
    action?: DialogAction;
    name?: string;
    error?: string;
    onConfirm?: () => void;
    onCancel?: () => void;
    onClose?: () => void;
  };

  let {
    open = false,
    title = "",
    message = "",
    action = null,
    name = $bindable(),
    error = "",
    onConfirm = () => {},
    onCancel = () => {},
    onClose = () => {},
  }: Props = $props();

  const lang = getContext<{ value: LangKey }>("lang");
  const t = $derived(TEXTS[lang.value].app);
</script>

<Dialog
  open={open}
  title={title}
  message={message}
  onConfirm={onConfirm}
  onCancel={onCancel}
  onClose={onClose}
  class="fusion-dialog"
>
  <div class="mt-3 space-y-3">
    {#if action === "save"}
      <Field
        label={t.fields.scriptNameLabel}
        bind:value={name}
        placeholder={t.fields.scriptNamePlaceholder}
      />
      {#if error}
        <p class="text-xs text-[var(--color-text-danger)]">{error}</p>
      {/if}
    {/if}
  </div>
</Dialog>
