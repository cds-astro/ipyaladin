import { convertOptionNamesToCamelCase } from "../utils";
import A from "../aladin_lite";

export default class MessageHandler {
  constructor(aladin, model) {
    this.aladin = aladin;
    this.model = model;
  }

  handleChangeFoV(msg) {
    this.aladin.setFoV(msg["fov"]);
  }

  handleGotoRaDec(msg) {
    this.aladin.gotoRaDec(msg["ra"], msg["dec"]);
  }

  handleSynchronizeWCS() {
    const wcs = this.aladin.getViewWCS();
    console.log(wcs);
    this.model.set("_wcs", wcs);
    this.model.save_changes();
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
    const regions = msg["regions_infos"];
    const graphic_options = convertOptionNamesToCamelCase(
      msg["graphic_options"] || {},
    );
    if (!graphic_options["color"]) graphic_options["color"] = "red";
    const overlay = A.graphicOverlay(graphic_options);
    this.aladin.addOverlay(overlay);
    for (const region of regions) {
      const infos = region["infos"];
      switch (region["region_type"]) {
        case "stcs":
          overlay.addFootprints(
            A.footprintsFromSTCS(infos.stcs, region.options),
          );
          break;
        case "circle":
          overlay.add(
            A.circle(infos.ra, infos.dec, infos.radius, region.options),
          );
          break;
        case "ellipse":
          overlay.add(
            A.ellipse(
              infos.ra,
              infos.dec,
              infos.a,
              infos.b,
              infos.theta,
              region.options,
            ),
          );
          break;
        case "line":
          overlay.add(
            A.line(
              infos.ra1,
              infos.dec1,
              infos.ra2,
              infos.dec2,
              region.options,
            ),
          );
          break;
        case "polygon":
          overlay.add(A.polygon(infos.vertices, region.options));
          break;
      }
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
