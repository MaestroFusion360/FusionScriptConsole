import "./setupLangContext";
import { fireEvent, render } from "@testing-library/svelte";
import { describe, expect, it } from "vitest";
import SidebarMenu from "../SidebarMenu.svelte";

describe("SidebarMenu", () => {
  it("renders app title and version", async () => {
    const { getByLabelText, findByText } = render(SidebarMenu, {
      props: { menu: [], activeItem: "", onSelect: () => {} },
    });

    await fireEvent.click(getByLabelText("Toggle navigation"));
    expect(await findByText("Fusion Script Console")).toBeTruthy();
    expect(await findByText((_, node) => {
      const text = node?.textContent ?? "";
      return text.startsWith("v");
    })).toBeTruthy();
  });
});
