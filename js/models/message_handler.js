import { convertOptionNamesToCamelCase } from "../utils";
import A from "../aladin_lite";

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
    this.aladin.addMOC(A.MOCFromURL(msg["moc_URL"], options));
  }

  handleAddMOCFromDict(msg) {
    const options = convertOptionNamesToCamelCase(msg["options"] || {});
    this.aladin.addMOC(A.MOCFromJSON(msg["moc_dict"], options));
  }

  handleAddOverlay(msg) {
    const infos = msg["infos"];
    const options = convertOptionNamesToCamelCase(msg["options"] || {});
    const overlay = A.graphicOverlay(options);
    this.aladin.addOverlay(overlay);
    switch (msg["region_type"]) {
      case "stcs":
        overlay.addFootprints(A.footprintsFromSTCS(infos.stcs));
        break;
      case "circle":
        overlay.add(A.circle(infos.ra, infos.dec, infos.radius));
        break;
      case "ellipse":
        overlay.add(
          A.ellipse(infos.ra, infos.dec, infos.a, infos.b, infos.theta),
        );
        break;
      case "line":
        overlay.add(A.line(infos.ra1, infos.dec1, infos.ra2, infos.dec2));
        break;
    }
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
