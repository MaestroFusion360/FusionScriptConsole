import type { SavedScript } from "./types";

export function upsertScript(options: {
  scripts: SavedScript[];
  name: string;
  code: string;
}): { scripts: SavedScript[]; activeName: string } {
  const { scripts, name, code } = options;
  const now = Date.now();
  const nextScripts = [...scripts];
  const index = nextScripts.findIndex((script) => script.name === name);

  if (index >= 0) {
    nextScripts[index] = {
      ...nextScripts[index],
      code,
      updatedAt: now,
    };
  } else {
    nextScripts.push({ name, code, updatedAt: now });
  }

  return { scripts: nextScripts, activeName: name };
}

export function removeScript(options: {
  scripts: SavedScript[];
  currentName: string;
}): { scripts: SavedScript[]; currentName: string; activeName: string } {
  const { scripts, currentName } = options;
  if (!currentName) {
    return { scripts, currentName: "", activeName: "" };
  }

  return {
    scripts: scripts.filter((script) => script.name !== currentName),
    currentName: "",
    activeName: "",
  };
}

export function buildExportContent(scripts: SavedScript[]): string {
  return scripts
    .map((script) => `"""${script.name}"""\n${script.code}`)
    .join("\n\n---\n\n");
}

export function parseImportContent(raw: string): SavedScript[] {
  if (!raw.trim()) return [];

  const blocks = raw
    .split(/\n\s*---\s*\n/g)
    .map((block) => block.trim())
    .filter(Boolean);

  const now = Date.now();
  const parsed: SavedScript[] = [];

  for (const block of blocks) {
    const lines = block.split("\n");
    const firstLine = lines[0]?.trim() ?? "";
    const match = firstLine.match(/^"""(.+?)"""$/);
    if (!match) continue;

    const name = match[1].trim();
    if (!name) continue;

    const code = lines.slice(1).join("\n");
    parsed.push({
      name,
      code,
      updatedAt: now,
    });
  }

  return parsed;
}

export function mergeImportedScripts(options: {
  current: SavedScript[];
  imported: SavedScript[];
}): SavedScript[] {
  const { current, imported } = options;
  if (!imported.length) return current;

  const byName = new Map(current.map((script) => [script.name, script]));
  for (const script of imported) {
    byName.set(script.name, script);
  }

  return Array.from(byName.values());
}
