import type { SavedScript } from "./types";

export const STORAGE_KEYS = {
  scripts: "fusion-script-console.scripts",
  legacy: "fusion-script-console.code",
  apiKey: "fusion-script-console.apiKey",
};

export function loadScripts(legacyName: string): SavedScript[] {
  const saved = localStorage.getItem(STORAGE_KEYS.scripts);
  if (saved) {
    try {
      return (JSON.parse(saved) as SavedScript[]) ?? [];
    } catch {
      return [];
    }
  }

  const legacy = localStorage.getItem(STORAGE_KEYS.legacy);
  if (!legacy) {
    return [];
  }

  localStorage.removeItem(STORAGE_KEYS.legacy);
  return [
    {
      name: legacyName,
      code: legacy,
      updatedAt: Date.now(),
    },
  ];
}

export function persistScripts(scripts: SavedScript[]) {
  localStorage.setItem(STORAGE_KEYS.scripts, JSON.stringify(scripts));
}

export function loadApiKey(): string {
  return localStorage.getItem(STORAGE_KEYS.apiKey) ?? "";
}

export function persistApiKey(apiKey: string) {
  localStorage.setItem(STORAGE_KEYS.apiKey, apiKey);
}
