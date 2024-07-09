/**
 * Run the notebooks of the examples folder
 */

import { expect, test, galata } from "@jupyterlab/galata";
import { setTimeout } from "timers/promises";
import * as path from "path";

// request and tmpPath are Playwright fixtures
test("1-Getting-Started", async ({ page, request, tmpPath }) => {
  // Import notebook 1
  const content = galata.newContentsHelper(request);
  const filename = "1_Getting_Started.ipynb";
  await content.uploadFile(
    path.resolve(__dirname, `../../examples/${filename}`),
    `${tmpPath}/${filename}`,
  );
  // Activate notebook
  await page.notebook.openByPath(`${tmpPath}/${filename}`);
  await page.notebook.activate(filename);
  // Wait until kernel is ready
  await page.waitForSelector(
    "#jp-main-statusbar >> text=Python 3 (ipykernel) | Idle",
  );
  // Execute all cells
  await page.notebook.runCellByCell();
  // Wait for Aladin to pop
  await setTimeout(3000); // 3s
  // Scroll to the top of the notebook
  page.notebook.getCellLocator(2);
  page.mouse.wheel(0, -2000);
  // Save
  await page.notebook.save();
  // And check snapshot (maybe we should clip to div jp-main-dock-panel)
  expect(await page.screenshot()).toMatchSnapshot();
});
