import MessageHandler from "./message_handler";
import { divNumber, setDivNumber, Lock, setDivHeight } from "../utils";

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
   * Updates the view center rotation in the model.
   * WARNING: This method doesn't call model.save_changes()!
   *
   * The python rotation traitlet is updated when:
   * - the user drag the view (positionChanged occuring).
   * - the user dbl click inside the view which resets the rotation to 0.
   */
  updateRotation() {
    if (!this.isLastDiv()) return;
    this.model.set("_rotation", this.aladin.getRotation());
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
    /* Position Control */
    // there are two ways of changing the target, one from the javascript side, and
    // one from the python side. We have to instantiate two listeners for these, but
    // the gotoObject call should only happen once. The two booleans prevent the two
    // listeners from triggering each other and creating a buggy loop.

    /* ----------------------- */
    /* Aladin events listeners */
    /* ----------------------- */
    // Event triggered when the user moves the map in Aladin Lite
    this.aladin.on("positionChanged", (position) => {
      if (pyTargetLock.locked) {
        pyTargetLock.unlock();
        return;
      }
      jsTargetLock.lock();

      const raDec = [position.ra, position.dec];
      this.updateWCS();
      // When dragging the view, north to east position angle might changes because
      // the spherical rotation does not keep the north pole up.
      this.updateRotation();
      this.model.set("_target", `${raDec[0]} ${raDec[1]}`);
      this.model.save_changes();
    });

    /* Field of View control */
    this.aladin.on("zoomChanged", (fov) => {
      // fov MUST be cast into float in order to be sent to the model
      this.model.set("_fov", parseFloat(fov.toFixed(5)));

      this.updateWCS();
      this.update2AxisFoV();
      if (!this.isLastDiv()) return;
      this.model.save_changes();
    });

    this.aladin.on("cooFrameChanged", () => {
      this.updateWCS();
      this.model.save_changes();
    });

    this.aladin.on("projectionChanged", () => {
      this.updateWCS();
      this.model.save_changes();
    });

    this.aladin.on("layerChanged", (imageLayer, layerName, state) => {
      if (layerName === "base")
        this.model.set("_survey_body", imageLayer.hipsBody || "sky");
      if (layerName !== "base" || state !== "ADDED") return;
      this.updateWCS();
      this.model.set("_base_layer_last_view", imageLayer.id);
      this.model.save_changes();
    });

    this.aladin.on("resizeChanged", (width, height) => {
      // Skip resize event when the div is hidden
      if (width === 1 && height === 1) {
        this.model.set("_is_reduced", true);
        this.model.save_changes();
        return;
      } else this.model.set("_is_reduced", false);
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

    this.aladin.on("rotationChanged", (_) => {
      this.updateRotation();
      if (!this.isLastDiv()) return;
      this.model.save_changes();
    });

    this.aladin.on("objectClicked", (clicked) => {
      if (clicked) {
        let clickedContent = {
          // the coordinates are in 'source' for footprints
          ra: clicked["ra"] || clicked["source"]["ra"],
          dec: clicked["dec"] || clicked["source"]["dec"],
        };
        if (clicked["data"] !== undefined) {
          clickedContent["data"] = clicked["data"];
        }
        if (clicked["source"] !== undefined) {
          clickedContent["data"] = clicked["source"]["data"];
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

    // A better way would be to listen to a "dblclick" event through aladin.on
    this.aladin.view.catalogCanvas.addEventListener("dblclick", (e) => {
      this.updateRotation();
      this.model.save_changes();
    });

    /* ----------------------- */
    /* Traits listeners        */
    /* ----------------------- */
    const jsTargetLock = new Lock();
    const pyTargetLock = new Lock();

    // This dictionary stores the handlers executed
    // when a trait has changed on the python side.
    // key is the name of the trait
    // value is the callback executed on change, it takes
    // the new value of the trait as single input param
    this.traitHandlers = {
      /* Target control */
      _target: (target) => {
        if (jsTargetLock.locked) {
          jsTargetLock.unlock();
          return;
        }
        pyTargetLock.lock();

        const raDec = target.split(" ");
        this.aladin.gotoRaDec(raDec[0], raDec[1]);
      },
      _fov: (fov) => {
        // zoomChanged is not triggered if the zoom does not change
        // from aladin inner state. This prevents having an infinite loop
        this.aladin.setFoV(fov);

        // Update WCS and FoV only if this is the last div
        this.updateWCS();
        this.update2AxisFoV();
        this.model.save_changes();
      },
      /* Rotation control */
      _rotation: (rotation) => {
        // And propagate it to Aladin Lite
        this.aladin.setRotation(rotation);

        // Update WCS and FoV only if this is the last div
        this.updateWCS();
        this.update2AxisFoV();
        this.model.save_changes();
      },
      /* Div control */
      _height: (height) => {
        setDivHeight(height, this.aladinDiv);
        // Update WCS and FoV only if this is the last div
        this.updateWCS();
        this.update2AxisFoV();
        this.model.save_changes();
      },
      coo_frame: (frame) => {
        this.aladin.setFrame(frame);
      },
      survey: (survey) => {
        this.aladin.setImageSurvey(survey);
      },
      overlay_survey: (survey) => {
        if (survey !== "") {
          this.aladin.setOverlayImageLayer(survey);
        }
      },
      overlay_survey_opacity: (opacity) => {
        let overlay = this.aladin.getOverlayImageLayer();

        if (overlay) {
          overlay.setAlpha(opacity);
        }
      },
    };

    for (var trait in this.traitHandlers) {
      let handler = this.traitHandlers[trait];
      this.model.on("change:" + trait, (_, value) => handler(value));
    }

    /* Aladin functionalities */
    // custom events handlers
    this.eventHandlers = {
      add_marker: this.messageHandler.handleAddMarker,
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
    for (var trait in this.traitHandlers) {
      this.model.off("change:" + trait);
    }
    this.model.off("msg:custom");
  }
}
