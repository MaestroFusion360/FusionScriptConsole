import "./setupLangContext";
import { render } from "@testing-library/svelte";
import { describe, expect, it } from "vitest";
import OutputPanel from "../OutputPanel.svelte";

describe("OutputPanel", () => {
  it("renders output header and hint when empty", () => {
    const { getByText } = render(OutputPanel, {
      props: { output: "", lastError: "" },
    });

    expect(getByText("Output")).toBeTruthy();
    expect(getByText("No output yet")).toBeTruthy();
  });

  it("shows last error when provided", () => {
    const { getByText } = render(OutputPanel, {
      props: { output: "OK", lastError: "Boom" },
    });

    expect(getByText("Boom")).toBeTruthy();
  });
});
