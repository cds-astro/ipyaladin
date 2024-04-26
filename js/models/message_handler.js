import { A, convertOptionNamesToCamelCase } from "../utils";

export default class MessageHandler {
  constructor(aladin) {
    this.aladin = aladin;
  }

  handleChangeFoV(msg) {
    this.aladin.setFoV(msg["fov"]);
  }

  handleGotoRaDec(msg) {
    this.aladin.gotoRaDec(msg["ra"], msg["dec"]);
  }

  handleAddCatalogFromURL(msg) {
    const options = convertOptionNamesToCamelCase(msg["options"] || {});
    this.aladin.addCatalog(A.catalogFromURL(msg["votable_URL"], options));
  }

  handleAddMOCFromURL(msg) {
    const options = convertOptionNamesToCamelCase(msg["options"] || {});
    if (options["lineWidth"] === undefined) options["lineWidth"] = 3;
    this.aladin.addMOC(A.MOCFromURL(msg["moc_URL"], options));
  }

  handleAddMOCFromDict(msg) {
    const options = convertOptionNamesToCamelCase(msg["options"] || {});
    if (options["lineWidth"] === undefined) options["lineWidth"] = 3;
    this.aladin.addMOC(A.MOCFromJSON(msg["moc_dict"], options));
  }

  handleAddOverlayFromSTCS(msg) {
    const overlayOptions = convertOptionNamesToCamelCase(
      msg["overlay_options"] || {},
    );
    const stcString = msg["stc_string"];
    const overlay = A.graphicOverlay(overlayOptions);
    this.aladin.addOverlay(overlay);
    overlay.addFootprints(A.footprintsFromSTCS(stcString));
  }

  handleChangeColormap(msg) {
    this.aladin.getBaseImageLayer().setColormap(msg["colormap"]);
  }

  handleGetJPGThumbnail() {
    this.aladin.exportAsPNG();
  }

  handleTriggerRectangularSelection() {
    this.aladin.select();
  }

  handleAddTable(msg, buffers) {
    const options = convertOptionNamesToCamelCase(msg["options"] || {});
    const buffer = buffers[0].buffer;
    const decoder = new TextDecoder("utf-8");
    const blob = new Blob([decoder.decode(buffer)]);
    const url = URL.createObjectURL(blob);
    A.catalogFromURL(
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
