export default class MessageHandler {
  constructor(A, aladin) {
    this.A = A;
    this.aladin = aladin;
  }

  handleChangeFoV(fov) {
    this.aladin.setFoV(fov);
  }

  handleGotoRaDec(ra, dec) {
    this.aladin.gotoRaDec(ra, dec);
  }

  handleAddCatalogFromURL(votableURL, options) {
    this.aladin.addCatalog(this.A.catalogFromURL(votableURL, options));
  }

  handleAddMOCFromURL(mocURL, options) {
    if (options["lineWidth"] === undefined) {
      options["lineWidth"] = 3;
    }
    this.aladin.addMOC(this.A.MOCFromURL(mocURL, options));
  }

  handleAddMOCFromDict(mocDict, options) {
    if (options["lineWidth"] === undefined) {
      options["lineWidth"] = 3;
    }
    this.aladin.addMOC(this.A.MOCFromJSON(mocDict, options));
  }

  handleAddOverlayFromSTCS(overlayOptions, stcString) {
    let overlay = this.A.graphicOverlay(overlayOptions);
    this.aladin.addOverlay(overlay);
    overlay.addFootprints(this.A.footprintsFromSTCS(stcString));
  }

  handleChangeColormap(colormap) {
    this.aladin.getBaseImageLayer().setColormap(colormap);
  }

  handleGetJPGThumbnail() {
    this.aladin.exportAsPNG();
  }

  handleTriggerRectangularSelection() {
    this.aladin.select();
  }

  handleAddTable(buffer, options) {
    let tableBytes = buffer;
    let decoder = new TextDecoder("utf-8");
    let blob = new Blob([decoder.decode(tableBytes)]);
    let url = URL.createObjectURL(blob);
    this.A.catalogFromURL(
      url,
      Object.assign(options, { onClick: "showTable" }),
      (catalog) => {
        this.aladin.addCatalog(catalog);
      },
      false,
    );
    URL.revokeObjectURL(url);
  }
}
