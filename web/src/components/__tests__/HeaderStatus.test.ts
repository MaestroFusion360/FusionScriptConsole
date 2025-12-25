import "./setupLangContext";
import { render } from "@testing-library/svelte";
import { describe, expect, it } from "vitest";
import HeaderStatus from "../HeaderStatus.svelte";

describe("HeaderStatus", () => {
  it("renders brand, title, and status label", () => {
    const { getByText } = render(HeaderStatus, {
      props: { statusLabel: "Online", statusClass: "status-ok" },
    });

    expect(getByText("Fusion API Server")).toBeTruthy();
    expect(getByText("Fusion Script Console")).toBeTruthy();
    expect(getByText("Online")).toBeTruthy();
  });
});
