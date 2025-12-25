import "./setupLangContext";
import { render } from "@testing-library/svelte";
import { describe, expect, it } from "vitest";
import ScriptDialog from "../ScriptDialog.svelte";

describe("ScriptDialog", () => {
  it("renders save dialog with name field", () => {
    const { getByText, getByLabelText } = render(ScriptDialog, {
      props: {
        open: true,
        title: "Save script",
        message: "Save the current script to local storage under a name.",
        action: "save",
        name: "Test",
      },
    });

    expect(getByText("Save script")).toBeTruthy();
    expect(getByLabelText("Script name")).toBeTruthy();
  });

  it("renders delete dialog without name field", () => {
    const { getByText, queryByLabelText } = render(ScriptDialog, {
      props: {
        open: true,
        title: "Delete script",
        message:
          "Delete the selected script from the list and clear the editor?",
        action: "delete",
      },
    });

    expect(getByText("Delete script")).toBeTruthy();
    expect(queryByLabelText("Script name")).toBeNull();
  });
});
