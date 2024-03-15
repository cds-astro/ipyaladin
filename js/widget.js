import A from "https://esm.sh/aladin-lite@3.3.3-beta";
import "./widget.css";

let idxView = 0;

function convert_pyname_to_jsname(pyname) {
  let temp = pyname.split("_");
  for (let i = 1; i < temp.length; i++) {
    temp[i] = temp[i].charAt(0).toUpperCase() + temp[i].slice(1);
  }
  return temp.join("");
}

async function initialize({ model }) {
  await A.init;
}

function render({ model, el }) {
  /* ------------------- */
  /* View -------------- */
  /* ------------------- */

  let init_options = {};
  model.get("init_options").forEach((option_name) => {
    init_options[convert_pyname_to_jsname(option_name)] =
      model.get(option_name);
  });

  let aladinDiv = document.createElement("div");
  aladinDiv.classList.add("aladin-widget");
  aladinDiv.style.height = `${init_options["height"]}px`;

  aladinDiv.id = `aladin-lite-div-${idxView}`;
  let aladin = new A.aladin(aladinDiv, init_options);
  idxView += 1;

  el.appendChild(aladinDiv);

  /* ------------------- */
  /* Listeners --------- */
  /* ------------------- */

  /* Position Control */
  // there are two ways of changing the target, one from the javascript side, and
  // one from the python side. We have to instantiate two listeners for these, but
  // the gotoObject call should only happen once. The two booleans prevent the two
  // listeners from triggering each other and creating a buggy loop. The same trick
  // is also necessary for the field of view.
  let target_js = false;
  let target_py = false;

  aladin.on("positionChanged", (position) => {
    if (!target_py) {
      target_js = true;
      model.set("target", `${position.ra} ${position.dec}`);
      model.save_changes();
    } else {
      target_py = false;
    }
  });

  model.on("change:target", () => {
    if (!target_js) {
      target_py = true;
      let target = model.get("target");
      aladin.gotoObject(target);
    } else {
      target_js = false;
    }
  });

  /* Field of View control */
  let fov_py = false;
  let fov_js = false;

  aladin.on("zoomChanged", (fov) => {
    if (!fov_py) {
      fov_js = true;
      // fov MUST be cast into float in order to be sent to the model
      model.set("fov", parseFloat(fov.toFixed(5)));
      model.save_changes();
    } else {
      fov_py = false;
    }
  });

  model.on("change:fov", () => {
    if (!fov_js) {
      fov_py = true;
      let fov = model.get("fov");
      aladin.setFoV(fov);
    } else {
      fov_js = false;
    }
  });

  /* Div control */

  model.on("change:height", () => {
    let height = model.get("height");
    aladinDiv.style.height = `${height}px`;
  });

  /* Aladin callbacks */

  aladin.on("objectHovered", (object) => {
    if (object["data"] != undefined) {
      model.send({
        event_type: "object_hovered",
        content: {
          ra: object["ra"],
          dec: object["dec"],
        },
      });
    }
  });

  aladin.on("objectClicked", (clicked) => {
    let clicked_content = {
      ra: clicked["ra"],
      dec: clicked["dec"],
    };
    if (clicked["data"] !== undefined) {
      clicked_content["data"] = clicked["data"];
    }
    model.set("clicked", clicked_content);
    // send a custom message in case the user wants to define their own callbacks
    model.send({
      event_type: "object_clicked",
      content: clicked_content,
    });
    model.save_changes();
  });

  aladin.on("click", (click_content) => {
    model.send({
      event_type: "click",
      content: click_content,
    });
  });

  aladin.on("select", (catalogs) => {
    let objects_data = [];
    // TODO: this flattens the selection. Each object from different
    // catalogs are entered in the array. To change this, maybe change
    // upstream what is returned upon selection?
    catalogs.forEach((catalog) => {
      catalog.forEach((object) => {
        objects_data.push({
          ra: object.ra,
          dec: object.dec,
          data: object.data,
          x: object.x,
          y: object.y,
        });
      });
    });
    model.send({
      event_type: "select",
      content: objects_data,
    });
  });

  /* Aladin functionalities */

  model.on("change:coo_frame", () => {
    aladin.setFrame(model.get("coo_frame"));
  });

  model.on("change:survey", () => {
    aladin.setImageSurvey(model.get("survey"));
  });

  model.on("change:overlay_survey", () => {
    aladin.setOverlayImageLayer(model.get("overlay_survey"));
  });

  model.on("change:overlay_survey_opacity", () => {
    aladin.getOverlayImageLayer().setAlpha(model.get("overlay_survey_opacity"));
  });

  model.on("msg:custom", (msg) => {
    let options = {};
    switch (msg["event_name"]) {
      case "add_catalog_from_URL":
        aladin.addCatalog(A.catalogFromURL(msg["votable_URL"], msg["options"]));
        break;
      case "add_MOC_from_URL":
        // linewidth = 3 is easier to see than the default 1 from upstream
        options = msg["options"];
        if (options["lineWidth"] === undefined) {
          options["lineWidth"] = 3;
        }
        aladin.addMOC(A.MOCFromURL(msg["moc_URL"], options));
        break;
      case "add_MOC_from_dict":
        // linewidth = 3 is easier to see than the default 1 from upstream
        options = msg["options"];
        if (options["lineWidth"] === undefined) {
          options["lineWidth"] = 3;
        }
        aladin.addMOC(A.MOCFromJSON(msg["moc_dict"], options));
        break;
      case "add_overlay_from_stcs":
        let overlay = A.graphicOverlay(msg["overlay_options"]);
        aladin.addOverlay(overlay);
        overlay.addFootprints(A.footprintsFromSTCS(msg["stc_string"]));
        break;
      case "change_colormap":
        aladin.getBaseImageLayer().setColormap(msg["colormap"]);
        break;
      case "get_JPG_thumbnail":
        aladin.exportAsPNG();
        break;
      case "trigger_rectangular_selection":
        aladin.select();
        break;
      case "add_table":
        let table_bytes = model.get("_table");
        let decoder = new TextDecoder("utf-8");
        let blob = new Blob([decoder.decode(table_bytes)]);
        let url = URL.createObjectURL(blob);
        A.catalogFromURL(
          url,
          Object.assign(msg.options, { onClick: "showTable" }),
          (catalog) => {
            aladin.addCatalog(catalog);
          },
          false,
        );
        URL.revokeObjectURL(url);
        break;
    }
  });

  return () => {
    // need to unsubscribe the listeners
    model.off("change:target");
    model.off("change:fov");
    model.off("change:height");
    model.off("change:coo_frame");
    model.off("change:survey");
    model.off("change:overlay_survey");
    model.off("change:overlay_survey_opacity");
    model.off("change:trigger_event");
    model.off("change:_table");
    model.off("msg:custom");

    aladin.off("positionChanged");
    aladin.off("zoomChanged");
    aladin.off("objectHovered");
    aladin.off("objectClicked");
    aladin.off("click");
    aladin.off("select");
  };
}

export default { initialize, render };
