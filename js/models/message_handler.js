import { camelCaseToSnakeCase } from "../utils";

export default class MessageHandler {
  constructor(A, aladin) {
    this.A = A;
    this.aladin = aladin;
  }

  handleChangeFoV(msg) {
    this.aladin.setFoV(msg["fov"]);
  }

  handleGotoRaDec(msg) {
    this.aladin.gotoRaDec(msg["ra"], msg["dec"]);
  }

  handleAddCatalogFromURL(msg) {
    const options = MessageHandler.parseOptions(msg["options"] || {});
    this.aladin.addCatalog(this.A.catalogFromURL(msg["votable_URL"], options));
  }

  handleAddMOCFromURL(msg) {
    const options = MessageHandler.parseOptions(msg["options"] || {});
    if (options["lineWidth"] === undefined) options["lineWidth"] = 3;
    this.aladin.addMOC(this.A.MOCFromURL(msg["moc_URL"], options));
  }

  handleAddMOCFromDict(msg) {
    const options = MessageHandler.parseOptions(msg["options"] || {});
    if (options["lineWidth"] === undefined) options["lineWidth"] = 3;
    this.aladin.addMOC(this.A.MOCFromJSON(msg["moc_dict"], options));
  }

  handleAddOverlayFromSTCS(msg) {
    const overlayOptions = MessageHandler.parseOptions(
      msg["overlay_options"] || {},
    );
    const stcString = msg["stc_string"];
    const overlay = this.A.graphicOverlay(overlayOptions);
    this.aladin.addOverlay(overlay);
    overlay.addFootprints(this.A.footprintsFromSTCS(stcString));
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
    const options = MessageHandler.parseOptions(msg["options"] || {});
    const buffer = buffers[0].buffer;
    const decoder = new TextDecoder("utf-8");
    const blob = new Blob([decoder.decode(buffer)]);
    const url = URL.createObjectURL(blob);
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

  static parseOptions(options) {
    for (const optionName in options) {
      const convertedOptionName = camelCaseToSnakeCase(optionName);
      options[convertedOptionName] = options[optionName];
    }
    return options;
  }
}
