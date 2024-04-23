import MessageHandler from "./message_handler";

export default class EventHandler {
  constructor(A, aladin, model) {
    this.A = A;
    this.aladin = aladin;
    this.model = model;
    this.messageHandler = new MessageHandler(A, aladin);
  }

  subscribeAll() {
    /* ------------------- */
    /* Listeners --------- */
    /* ------------------- */

    /* Position Control */
    // there are two ways of changing the target, one from the javascript side, and
    // one from the python side. We have to instantiate two listeners for these, but
    // the gotoObject call should only happen once. The two booleans prevent the two
    // listeners from triggering each other and creating a buggy loop. The same trick
    // is also necessary for the field of view.

    /* Target control */
    let targetJs = false;
    let targetPy = false;

    // Event triggered when the user moves the map in Aladin Lite
    this.aladin.on("positionChanged", () => {
      if (targetPy) {
        targetPy = false;
        return;
      }
      targetJs = true;
      const raDec = this.aladin.getRaDec();
      this.model.set("_target", `${raDec[0]} ${raDec[1]}`);
      this.model.set("shared_target", `${raDec[0]} ${raDec[1]}`);
      this.model.save_changes();
    });

    // Event triggered when the target is changed from the Python side using jslink
    this.model.on("change:shared_target", () => {
      if (targetJs) {
        targetJs = false;
        return;
      }
      targetPy = true;
      const target = this.model.get("shared_target");
      const [ra, dec] = target.split(" ");
      this.aladin.gotoRaDec(ra, dec);
    });

    /* Field of View control */
    let fovJs = false;
    let fovPy = false;

    this.aladin.on("zoomChanged", (fov) => {
      if (fovPy) {
        fovPy = false;
        return;
      }
      fovJs = true;
      // fov MUST be cast into float in order to be sent to the model
      this.model.set("_fov", parseFloat(fov.toFixed(5)));
      this.model.set("shared_fov", parseFloat(fov.toFixed(5)));
      this.model.save_changes();
    });

    this.model.on("change:shared_fov", () => {
      if (fovJs) {
        fovJs = false;
        return;
      }
      fovPy = true;
      let fov = this.model.get("shared_fov");
      this.aladin.setFoV(fov);
    });

    /* Div control */

    this.model.on("change:height", () => {
      let height = this.model.get("height");
      aladinDiv.style.height = `${height}px`;
    });

    /* Aladin callbacks */

    this.aladin.on("objectHovered", (object) => {
      if (object["data"] !== undefined) {
        this.model.send({
          event_type: "object_hovered",
          content: {
            ra: object["ra"],
            dec: object["dec"],
          },
        });
      }
    });

    this.aladin.on("objectClicked", (clicked) => {
      let clickedContent = {
        ra: clicked["ra"],
        dec: clicked["dec"],
      };
      if (clicked["data"] !== undefined) {
        clickedContent["data"] = clicked["data"];
      }
      this.model.set("clicked", clickedContent);
      // send a custom message in case the user wants to define their own callbacks
      this.model.send({
        event_type: "object_clicked",
        content: clickedContent,
      });
      this.model.save_changes();
    });

    this.aladin.on("click", (clickContent) => {
      this.model.send({
        event_type: "click",
        content: clickContent,
      });
    });

    this.aladin.on("select", (catalogs) => {
      let objectsData = [];
      // TODO: this flattens the selection. Each object from different
      // catalogs are entered in the array. To change this, maybe change
      // upstream what is returned upon selection?
      catalogs.forEach((catalog) => {
        catalog.forEach((object) => {
          objectsData.push({
            ra: object.ra,
            dec: object.dec,
            data: object.data,
            x: object.x,
            y: object.y,
          });
        });
      });
      this.model.send({
        event_type: "select",
        content: objectsData,
      });
    });

    /* Aladin functionalities */

    this.model.on("change:coo_frame", () => {
      this.aladin.setFrame(this.model.get("coo_frame"));
    });

    this.model.on("change:survey", () => {
      this.aladin.setImageSurvey(this.model.get("survey"));
    });

    this.model.on("change:overlay_survey", () => {
      this.aladin.setOverlayImageLayer(this.model.get("overlay_survey"));
    });

    this.model.on("change:overlay_survey_opacity", () => {
      this.aladin
        .getOverlayImageLayer()
        .setAlpha(this.model.get("overlay_survey_opacity"));
    });

    this.model.on("msg:custom", (msg, buffers) => {
      let options = {};
      switch (msg["event_name"]) {
        case "change_fov":
          this.messageHandler.handleChangeFoV(msg["fov"]);
          break;
        case "goto_ra_dec":
          this.messageHandler.handleGotoRaDec(msg["ra"], msg["dec"]);
          break;
        case "add_catalog_from_URL":
          this.messageHandler.handleAddCatalogFromURL(
            msg["votable_URL"],
            msg["options"],
          );
          break;
        case "add_MOC_from_URL":
          this.messageHandler.handleAddMOCFromURL(
            msg["moc_URL"],
            msg["options"],
          );
          break;
        case "add_MOC_from_dict":
          this.messageHandler.handleAddMOCFromDict(
            msg["moc_dict"],
            msg["options"],
          );
          break;
        case "add_overlay_from_stcs":
          this.messageHandler.handleAddOverlayFromSTCS(
            msg["overlay_options"],
            msg["stc_string"],
          );
          break;
        case "change_colormap":
          this.messageHandler.handleChangeColormap(msg["colormap"]);
          break;
        case "get_JPG_thumbnail":
          this.messageHandler.handleGetJPGThumbnail();
          break;
        case "trigger_rectangular_selection":
          this.messageHandler.handleTriggerRectangularSelection();
          break;
        case "add_table":
          this.messageHandler.handleAddTable(buffers[0].buffer, msg.options);
          break;
      }
    });
  }

  unsubscribeAll() {
    this.model.off("change:shared_target");
    this.model.off("change:fov");
    this.model.off("change:height");
    this.model.off("change:coo_frame");
    this.model.off("change:survey");
    this.model.off("change:overlay_survey");
    this.model.off("change:overlay_survey_opacity");
    this.model.off("change:trigger_event");
    this.model.off("msg:custom");

    this.aladin.off("positionChanged");
    this.aladin.off("zoomChanged");
    this.aladin.off("objectHovered");
    this.aladin.off("objectClicked");
    this.aladin.off("click");
    this.aladin.off("select");
  }
}
