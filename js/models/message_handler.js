import { convertOptionNamesToCamelCase } from "../utils";
import A from "../aladin_lite";

let imageCount = 0;

export default class MessageHandler {
  constructor(aladin, model) {
    this.aladin = aladin;
    this.model = model;
  }

  handleAddMarker(msg) {
    const options = convertOptionNamesToCamelCase(msg["options"] || {});
    // default name
    if (!options.name) options.name = "markers";
    // create catalog
    const catalog = A.catalog(options);
    this.aladin.addCatalog(catalog);
    const pythonMarkers = msg["markers"];
    const markers = [];
    for (const marker of pythonMarkers) {
      markers.push(
        A.marker(marker["lon"], marker["lat"], {
          useMarkerDefaultIcon: options["useMarkerDefaultIcon"] | false,
          popupTitle: marker["title"],
          popupDesc: marker["description"],
        }),
      );
    }
    catalog.addSources(markers);
  }

  handleChangeFoV(msg) {
    this.aladin.setFoV(msg["fov"]);
  }

  handleGotoRaDec(msg) {
    this.aladin.gotoRaDec(msg["ra"], msg["dec"]);
  }

  async handleSaveViewAsImage(msg) {
    const path = msg["path"];
    const format = msg["format"];
    const withLogo = msg["with_logo"];
    const buffer = await this.aladin.getViewData(
      "arraybuffer",
      `image/${format}`,
      withLogo,
    );
    this.model.send(
      {
        event_type: "save_view_as_image",
        path: path,
      },
      null,
      [buffer],
    );
  }

  handleAddFits(msg, buffers) {
    const options = convertOptionNamesToCamelCase(msg["options"] || {});
    if (!options.name)
      options.name = `image_${String(++imageCount).padStart(3, "0")}`;
    const buffer = buffers[0];
    const blob = new Blob([buffer], { type: "application/octet-stream" });
    const url = URL.createObjectURL(blob);
    const image = this.aladin.createImageFITS(url, options, (ra, dec) => {
      this.aladin.gotoRaDec(ra, dec);
      console.info(`FITS located at ra: ${ra}, dec: ${dec}`);
      URL.revokeObjectURL(url);
    });
    this.aladin.setOverlayImageLayer(image, options.name);
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
          // remove default lineWidth when we switch to AL > 3.4.4
          region.options.lineWidth = region.options.lineWidth || 3;
          overlay.add(
            A.vector(
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

  handleTriggerSelection(msg) {
    let selectionType = msg["selection_type"];
    if (selectionType === "rectangle") selectionType = "rect";
    else if (selectionType === "polygon") selectionType = "poly";
    this.aladin.select(selectionType);
  }

  handleAddTable(msg, buffers) {
    const options = convertOptionNamesToCamelCase(msg["options"] || {});
    const circleOptions = convertOptionNamesToCamelCase(
      options.circleError || {},
    );
    const ellipseOptions = convertOptionNamesToCamelCase(
      options.ellipseError || {},
    );
    const buffer = buffers[0].buffer;
    const decoder = new TextDecoder("utf-8");
    const blob = new Blob([decoder.decode(buffer)]);
    const url = URL.createObjectURL(blob);
    options.onClick = "showTable";
    const shape = options.shape || "cross";
    if (Object.keys(circleOptions).length != 0) {
      options.shape = (source) => {
        if (source.data[circleOptions.radius]) {
          return A.circle(
            source.ra,
            source.dec,
            source.data[circleOptions.radius] * circleOptions.conversionRadius,
          );
        } else {
          return shape;
        }
      };
    }
    if (Object.keys(ellipseOptions).length != 0) {
      options.shape = (source) => {
        if (
          source.data[ellipseOptions.majAxis] &
          source.data[ellipseOptions.minAxis]
        ) {
          return A.ellipse(
            source.ra,
            source.dec,
            source.data[ellipseOptions.majAxis] *
              ellipseOptions.conversionMajAxis,
            source.data[ellipseOptions.minAxis] *
              ellipseOptions.conversionMinAxis,
            source.data[ellipseOptions.angle] * ellipseOptions.conversionAngle,
          );
        } else {
          return shape;
        }
      };
    }
    A.catalogFromURL(
      url,
      options,
      (catalog) => {
        this.aladin.addCatalog(catalog);
      },
      false,
    );
    URL.revokeObjectURL(url);
  }
}
