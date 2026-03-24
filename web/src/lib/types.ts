export type Status = "idle" | "running" | "ok" | "error";

export type SavedScript = {
  name: string;
  code: string;
  updatedAt: number;
};

export type ApiResponse = {
  ok?: boolean;
  output?: unknown;
  error?: string;
  result?: {
    output?: unknown;
    content?: Array<{ text?: string }>;
  };
};
