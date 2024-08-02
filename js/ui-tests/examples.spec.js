/**
 * Run the notebooks of the examples folder
 */

import { expect, test, galata } from "@jupyterlab/galata";
import * as path from "path";

async function openNotebook(page, request, tmpPath, notebookName) {
  const content = galata.newContentsHelper(request);
  const filename = notebookName;
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
  await page
    .getByRole("button", { name: "Toggle virtual scrollbar (" })
    .click();
}

async function uploadFitsFile(page, request, tmpPath, filePath) {
  const content = galata.newContentsHelper(request);
  const fitsFileName = path.basename(filePath);
  await content.uploadFile(
    path.resolve(__dirname, filePath),
    `${tmpPath}/${fitsFileName}`,
  );
}

async function gotoCell(page, cellNumber) {
  // await page.getByLabel('notebook content').getByText(`${cellNumber}`, {exact: true}).click();
  // await page.getElementsByClassName("jp-WindowedPanel-scrollbar-item").item(cellNumber).click();
  const elements = await page.$$(".jp-WindowedPanel-scrollbar-item");
  if (elements.length > cellNumber) {
    await elements[cellNumber].click();
  } else {
    console.log(`L'index ${cellNumber} est hors des limites.`);
  }
}

async function matchAladinCell(aladinCell) {
  expect(await aladinCell.screenshot()).toMatchSnapshot();
}

test("01_Getting_Started", async ({ page, request, tmpPath }) => {
  // Import notebook 1
  await openNotebook(page, request, tmpPath, "01_Getting_Started.ipynb");
  // Execute all cells
  await page.notebook.runCellByCell();
  // Wait for Aladin to pop
  await page.waitForTimeout(3000);
  // Scroll to the top of the notebook
  const aladinCell = await page.locator("canvas").nth(1);

  await gotoCell(page, 1);
  // And check snapshot (maybe we should clip to div jp-main-dock-panel)
  await matchAladinCell(aladinCell);
});

test("02_Base_Commands", async ({ page, request, tmpPath }) => {
  await uploadFitsFile(
    page,
    request,
    tmpPath + "/images/",
    "../../examples/images/m31.fits",
  );
  await openNotebook(page, request, tmpPath, "02_Base_Commands.ipynb");

  const aladinCell = await page.locator("canvas").nth(1);

  for (let i = 1; i < 7; i++) await page.notebook.runCell(i);
  await page.waitForTimeout(1000); // 1s
  for (let i = 7; i < 17; i++) await page.notebook.runCell(i);

  const targetLocator = await page.notebook.getCellLocator(8);
  // expect(await targetLocator.textContent()).toContain(
  //   "<SkyCoord (ICRS): (ra, dec) in deg\n" +
  //     "    (266.41681663, -29.00782497)>",
  // );

  const fovLocator = await page.notebook.getCellLocator(11);
  expect(await fovLocator.textContent()).toContain("2∘00′00′′");

  const cooFrameLocator = await page.notebook.getCellLocator(16);
  expect(await cooFrameLocator.textContent()).toContain("'ICRSd'");

  // Check first snapshot
  // await aladinCell.press("ArrowUp");
  // await page.notebook.save();
  await gotoCell(page, 5);
  await matchAladinCell(aladinCell);

  for (let i = 18; i < 21; i++) await page.notebook.runCell(i);

  // Check second snapshot
  // await aladinCell.press("ArrowUp");
  await gotoCell(page, 5);
  await matchAladinCell(aladinCell);

  // add_fits check
  await page.notebook.runCell(22);

  // Check third snapshot
  // await aladinCell.press("ArrowUp");
  await gotoCell(page, 5);
  await matchAladinCell(aladinCell);
});
