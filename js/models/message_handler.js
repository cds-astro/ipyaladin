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
    // Define default color for graphic overlay
    const overlay_color = options["color"] || options["fillColor"] || "red";
    const overlay = A.graphicOverlay({ color: overlay_color });
    this.aladin.addOverlay(overlay);
    switch (msg["region_type"]) {
      case "stcs":
        overlay.add(A.footprintsFromSTCS(infos.stcs, options));
        break;
      case "circle_pixel":
        [infos.ra, infos.dec] = this.aladin.pix2world(infos.x, infos.y, "ICRS");
        infos.radius = this.aladin.angularDist(
          infos.x,
          infos.y,
          infos.x + infos.radius,
          infos.y,
          "ICRS",
        );
      // Voluntary fallthrough
      case "circle_sky":
        overlay.add(A.circle(infos.ra, infos.dec, infos.radius, options));
        break;
      case "ellipse_pixel":
        [infos.ra, infos.dec] = this.aladin.pix2world(infos.x, infos.y, "ICRS");
        infos.a = this.aladin.angularDist(
          infos.x,
          infos.y,
          infos.x + infos.a,
          infos.y,
          "ICRS",
        );
        infos.b = this.aladin.angularDist(
          infos.x,
          infos.y,
          infos.x,
          infos.y + infos.b,
          "ICRS",
        );
      // Voluntary fallthrough
      case "ellipse_sky":
        overlay.add(
          A.ellipse(
            infos.ra,
            infos.dec,
            infos.a,
            infos.b,
            infos.theta,
            options,
          ),
        );
        break;
      case "line_pixel":
        [infos.ra1, infos.dec1] = this.aladin.pix2world(
          infos.x1,
          infos.y1,
          "ICRS",
        );
        [infos.ra2, infos.dec2] = this.aladin.pix2world(
          infos.x2,
          infos.y2,
          "ICRS",
        );
      // Voluntary fallthrough
      case "line_sky":
        overlay.add(
          A.line(infos.ra1, infos.dec1, infos.ra2, infos.dec2, options),
        );
        break;
      case "polygon_pixel":
        infos.vertices = infos.vertices.map(([x, y]) =>
          this.aladin.pix2world(x, y, "ICRS"),
        );
      // Voluntary fallthrough
      case "polygon_sky":
        overlay.add(A.polygon(infos.vertices, options));
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
