import { SvelteURL } from "svelte/reactivity";

import type { ApiResponse } from "./types";

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

export const HEALTH_POLL_MS = 2000;
export const HEALTH_TIMEOUT_MS = 1200;

export function wrapCode(source: string): string {
  const lines = source.split("\n");
  return ["def run(context):", ...lines.map((line) => `    ${line}`)].join(
    "\n"
  );
}

export function getHealthUrl(url: string): string | null {
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

export async function checkServerHealth(
  healthUrl: string,
  apiKey: string,
  timeoutMs: number = HEALTH_TIMEOUT_MS
): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    const cacheBuster = healthUrl.includes("?") ? "&" : "?";
    const response = await fetch(`${healthUrl}${cacheBuster}t=${Date.now()}`, {
      method: "GET",
      cache: "no-store",
      headers: { "X-API-Key": apiKey },
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response.ok;
  } catch {
    return false;
  }
}

export function safeJsonParse(
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

export function getResultText(data: ApiResponse): string | null {
  return (
    normalizeText(data.output) ??
    normalizeText(data.result?.output) ??
    normalizeText(data.result?.content?.[0]?.text) ??
    null
  );
}

export function buildPayload(options: {
  source: string;
  wrapInRun: boolean;
  autoImport: boolean;
}): string {
  const { source, wrapInRun, autoImport } = options;

  let header = "";
  if (autoImport) {
    const missing = AUTO_IMPORT_LINES.filter(
      (_, index) => !AUTO_IMPORT_RES[index].test(source)
    );
    if (missing.length) {
      header = `${missing.join("\n")}\n\n`;
    }
  }

  if (wrapInRun && !RUN_DEF_RE.test(source)) {
    return `${header}${wrapCode(source)}`;
  }

  return `${header}${source}`;
}
