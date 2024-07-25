/**
 * Run the notebooks of the examples folder
 */

import { expect, test, galata } from "@jupyterlab/galata";
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

  let wcsCellIdx = 4;

  for (let i = 0; i <= wcsCellIdx; i++) await page.notebook.runCell(i);
  await page.waitForTimeout(3000);

  let wcsCell = await page.notebook.getCellTextOutput(wcsCellIdx);
  expect(wcsCell[0]).toContain("CTYPE : 'RA---SIN'");
  expect(wcsCell[0]).toContain("NAXIS : 592  600");
});
