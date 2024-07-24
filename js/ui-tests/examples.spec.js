/**
 * Run the notebooks of the examples folder
 */

import { expect, test, galata } from "@jupyterlab/galata";
import { setTimeout } from "timers/promises";
import * as path from "path";

// request and tmpPath are Playwright fixtures
test("01_Getting_Started", async ({ page, request, tmpPath }) => {
  // Import notebook 1
  const content = galata.newContentsHelper(request);
  const filename = "01_Getting_Started.ipynb";
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
  await page.notebook.runCell(1);
  await page.notebook.runCell(2);
  await page.notebook.addCell("code", "");
  await page.notebook.runCell(3);
  // Wait for Aladin to pop
  await page.waitForTimeout(3000); // 3s
  // Scroll to the top of the notebook
  await page.getByLabel("Cells").getByRole("textbox").nth(4).press("ArrowUp");
  await page.getByLabel("Cells").getByRole("textbox").nth(3).press("ArrowUp");
  // Save
  await page.notebook.save();
  // And check snapshot (maybe we should clip to div jp-main-dock-panel)
  expect(await page.screenshot()).toMatchSnapshot();
});

test("11_Extracting_information_from_the_view", async ({
  page,
  request,
  tmpPath,
}) => {
  // Import notebook 4
  const content = galata.newContentsHelper(request);
  const filename = "11_Extracting_information_from_the_view.ipynb";
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

  for (let i = 0; i < 15; i++) await page.notebook.runCell(i);
  await page.waitForTimeout(3000);

  // Click on the Aladin widget to make the selection
  await page
    .locator("canvas")
    .nth(1)
    .click({
      position: {
        x: 319,
        y: 195,
      },
    });
  await page
    .locator("canvas")
    .nth(1)
    .click({
      position: {
        x: 354,
        y: 300,
      },
    });

  await page.notebook.runCell(16);
  // Fetch the cell content and check if the table is displayed
  const targetCellLocator = await page.notebook.getCellLocator(16);
  // Extract cell result
  const cellResult = await targetCellLocator.textContent();

  expect(cellResult).toContain("[<Table length=5>");
});
