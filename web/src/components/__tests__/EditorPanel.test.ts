import "./setupLangContext";
import { render } from "@testing-library/svelte";
import { describe, expect, it } from "vitest";
import EditorPanel from "../EditorPanel.svelte";

describe("EditorPanel", () => {
  it("renders server fields and script editor labels", () => {
    const { getByText, getByLabelText } = render(EditorPanel, {
      props: {
        serverUrl: "http://127.0.0.1:9100/api",
        apiKey: "secret",
        wrapInRun: true,
        code: "print('ok')",
      },
    });

    expect(getByText("Fusion API Server")).toBeTruthy();
    expect(getByText("Server URL")).toBeTruthy();
    expect(getByText("API Key")).toBeTruthy();
    expect(getByText("Python script")).toBeTruthy();
    expect(getByLabelText("Server URL")).toBeTruthy();
    expect(getByLabelText("API Key")).toBeTruthy();
  });
});
