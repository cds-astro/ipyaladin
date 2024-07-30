import MessageHandler from "./message_handler";
import { divNumber, setDivNumber, Lock } from "../utils";

export default class EventHandler {
  /**
   * Constructor for the EventHandler class.
   * @param aladin The Aladin instance
   * @param aladinDiv The Aladin div
   * @param model The model instance
   */
  constructor(aladin, aladinDiv, model) {
    this.aladin = aladin;
    this.aladinDiv = aladinDiv;
    this.model = model;
    this.messageHandler = new MessageHandler(aladin, model);
    this.currentDivNumber = parseInt(aladinDiv.id.split("-").pop());
  }

  /**
   * Checks if the current div is the last active div.
   * @returns {boolean}
   */
  isLastDiv() {
    if (this.currentDivNumber === divNumber) {
      return true;
    }
    let maxDiv = divNumber;
    for (let i = maxDiv; i >= 0; i--) {
      const alDiv = document.getElementById(`aladin-lite-div-${i}`);
      if (!alDiv) continue;
      if (alDiv.style.display !== "none") {
        maxDiv = i;
        break;
      }
    }
    setDivNumber(maxDiv);
    return this.currentDivNumber === maxDiv;
  }

  /**
   * Updates the WCS coordinates in the model.
   * WARNING: This method don't call model.save_changes()!
   */
  updateWCS() {
    if (!this.isLastDiv()) return;
    this.model.set("_wcs", this.aladin.getViewWCS());
  }

  /**
   * Updates the 2-axis FoV in the model.
   * WARNING: This method don't call model.save_changes()!
   */
  update2AxisFoV() {
    if (!this.isLastDiv()) return;
    const twoAxisFoV = this.aladin.getFov();
    this.model.set("_fov_xy", {
      x: twoAxisFoV[0],
      y: twoAxisFoV[1],
    });
  }

  /**
   * Subscribes to all the events needed for the Aladin Lite widget.
   */
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
    const jsTargetLock = new Lock();
    const pyTargetLock = new Lock();

    // Event triggered when the user moves the map in Aladin Lite
    this.aladin.on("positionChanged", (position) => {
      if (pyTargetLock.locked) {
        pyTargetLock.unlock();
        return;
      }
      jsTargetLock.lock();
      const raDec = [position.ra, position.dec];
      this.updateWCS();
      this.model.set("_target", `${raDec[0]} ${raDec[1]}`);
      this.model.save_changes();
    });

    this.model.on("change:_target", () => {
      if (jsTargetLock.locked) {
        jsTargetLock.unlock();
        return;
      }
      pyTargetLock.lock();
      let target = this.model.get("_target");
      const [ra, dec] = target.split(" ");
      this.aladin.gotoRaDec(ra, dec);
    });

    /* Field of View control */
    const jsFovLock = new Lock();
    const pyFovLock = new Lock();

    this.aladin.on("zoomChanged", (fov) => {
      if (pyFovLock.locked) {
        pyFovLock.unlock();
        return;
      }
      jsFovLock.lock();
      // fov MUST be cast into float in order to be sent to the model
      this.updateWCS();
      this.update2AxisFoV();
      this.model.set("_fov", parseFloat(fov.toFixed(5)));
      this.model.save_changes();
    });

    this.model.on("change:_fov", () => {
      if (jsFovLock.locked) {
        jsFovLock.unlock();
        return;
      }
      pyFovLock.lock();
      let fov = this.model.get("_fov");
      this.aladin.setFoV(fov);
    });

    this.aladin.on("layerChanged", (imageLayer, layerName, state) => {
      if (layerName !== "base" || state !== "ADDED") return;
      this.updateWCS();
      this.model.set("_base_layer_last_view", imageLayer.id);
      this.model.save_changes();
    });

    /* Div control */
    this.model.on("change:_height", () => {
      let height = this.model.get("_height");
      this.aladinDiv.style.height = `${height}px`;
      // Update WCS and FoV only if this is the last div
      this.updateWCS();
      this.update2AxisFoV();
      this.model.save_changes();
    });

    /* Aladin callbacks */

    this.aladin.on("cooFrameChanged", () => {
      this.updateWCS();
      this.model.save_changes();
    });

    this.aladin.on("projectionChanged", () => {
      this.updateWCS();
      this.model.save_changes();
    });

    this.aladin.on("resizeChanged", (width, height) => {
      // Skip resize event when the div is hidden
      if (width === 1 && height === 1) return;
      this.updateWCS();
      this.update2AxisFoV();
      this.model.set("_height", height);
      this.model.save_changes();
    });

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
      if (clicked) {
        let clickedContent = {
          ra: clicked["ra"],
          dec: clicked["dec"],
        };
        if (clicked["data"] !== undefined) {
          clickedContent["data"] = clicked["data"];
        }
        this.model.set("clicked_object", clickedContent);
        // send a custom message in case the user wants to define their own callbacks
        this.model.send({
          event_type: "object_clicked",
          content: clickedContent,
        });
        this.model.save_changes();
      }
    });

    this.aladin.on("click", (clickContent) => {
      this.model.send({
        event_type: "click",
        content: clickContent,
      });
    });

    this.aladin.on("select", (catalogs) => {
      const selectedObjects = catalogs.map((catalog) => {
        return catalog.map((object) => {
          return {
            ra: object.ra,
            dec: object.dec,
            data: object.data,
            x: object.x,
            y: object.y,
          };
        });
      });
      this.model.set("_selected_objects", selectedObjects);
      this.model.save_changes();

      // TODO: this flattens the selection. Each object from different
      // catalogs are entered in the array. To change this, maybe change
      // upstream what is returned upon selection?
      let objectsData = [];
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

    this.eventHandlers = {
      change_fov: this.messageHandler.handleChangeFoV,
      goto_ra_dec: this.messageHandler.handleGotoRaDec,
      save_view_as_image: this.messageHandler.handleSaveViewAsImage,
      add_fits: this.messageHandler.handleAddFits,
      add_catalog_from_URL: this.messageHandler.handleAddCatalogFromURL,
      add_MOC_from_URL: this.messageHandler.handleAddMOCFromURL,
      add_MOC_from_dict: this.messageHandler.handleAddMOCFromDict,
      add_overlay: this.messageHandler.handleAddOverlay,
      change_colormap: this.messageHandler.handleChangeColormap,
      get_JPG_thumbnail: this.messageHandler.handleGetJPGThumbnail,
      trigger_selection: this.messageHandler.handleTriggerSelection,
      add_table: this.messageHandler.handleAddTable,
    };

    this.model.on("msg:custom", (msg, buffers) => {
      const eventName = msg["event_name"];
      const handler = this.eventHandlers[eventName];
      if (handler) handler.call(this, msg, buffers);
      else throw new Error(`Unknown event name: ${eventName}`);
    });
  }

  /**
   * Unsubscribe from all the model events.
   * There is no need to unsubscribe from the Aladin Lite events.
   */
  unsubscribeAll() {
    this.model.off("change:_target");
    this.model.off("change:_fov");
    this.model.off("change:_height");
    this.model.off("change:coo_frame");
    this.model.off("change:survey");
    this.model.off("change:overlay_survey");
    this.model.off("change:overlay_survey_opacity");
    this.model.off("change:trigger_event");
    this.model.off("msg:custom");
  }
}
