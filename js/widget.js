import "./widget.css";
import EventHandler from "./models/event_handler";
import {
  divNumber,
  setDivHeight,
  setDivNumber,
  snakeCaseToCamelCase,
} from "./utils";
import A from "./aladin_lite";

function initAladinLite(model, el) {
  // Add 'aladin-lite-lm-container' class to the div container to apply the CSS styles in widget.css
  el.classList.add("aladin-lite-lm-container");

  setDivNumber(divNumber + 1);
  let initFromPython = model.get("_init_options");
  let initOptions = {};
  for (const key in initFromPython) {
    initOptions[snakeCaseToCamelCase(key)] = initFromPython[key];
  }

  let aladinDiv = document.createElement("div");
  aladinDiv.classList.add("aladin-widget");
  setDivHeight(model.get("_height"), aladinDiv);
  aladinDiv.id = `aladin-lite-div-${divNumber}`;
  let aladin = new A.aladin(aladinDiv, initOptions);
  el.appendChild(aladinDiv);

  return { aladin, aladinDiv };
}

async function initialize({ model }) {
  await A.init;
}

function render({ model, el }) {
  /* ------------------- */
  /* View -------------- */
  /* ------------------- */

  const { aladin, aladinDiv } = initAladinLite(model, el);

  const eventHandler = new EventHandler(aladin, aladinDiv, model);
  eventHandler.subscribeAll();

  // Traitlets have maybe been set on the python side, so we propagate them to aladin
  // Set the target again after the initialization to be sure that the target is set
  // from icrs coordinates because of the use of gotoObject in the Aladin Lite API
  let traitHandlers = eventHandler.traitHandlers;
  for (const trait in traitHandlers) {
    let value = model.get(trait);
    if (value !== null) {
      traitHandlers[trait](value);
    }
  }

  // Send fovXY and WCS traitlets to python
  const twoAxisFoV = { ...aladin.getFov() };
  model.set("_fov_xy", {
    x: twoAxisFoV[0],
    y: twoAxisFoV[1],
  });
  const wcs = { ...aladin.getViewWCS() };
  model.set("_wcs", wcs);

  // send colormap to python
  const cmap = aladin.getBaseImageLayer().getColorCfg().colormap;
  model.set("colormap", cmap);

  // Tell the widget is loaded so that all stored calls waiting can be executed
  model.set("_is_loaded", true);
  model.save_changes();

  return () => {
    // Need to unsubscribe the listeners
    eventHandler.unsubscribeAll();
  };
}

export default { initialize, render };
