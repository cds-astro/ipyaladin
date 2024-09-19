import "./widget.css";
import EventHandler from "./models/event_handler";
import { divNumber, setDivNumber, snakeCaseToCamelCase } from "./utils";
import A from "./aladin_lite";

function initAladinLite(model, el) {
  setDivNumber(divNumber + 1);
  let initFromPython = model.get("_init_options");
  let initOptions = {};
  for (const key in initFromPython) {
    initOptions[snakeCaseToCamelCase(key)] = initFromPython[key];
  }

  let aladinDiv = document.createElement("div");
  aladinDiv.classList.add("aladin-widget");
  aladinDiv.style.height = `${model.get("_height")}px`;

  aladinDiv.id = `aladin-lite-div-${divNumber}`;
  let aladin = new A.aladin(aladinDiv, initOptions);
  el.appendChild(aladinDiv);

  // Set the target again after the initialization to be sure that the target is set
  // from icrs coordinates because of the use of gotoObject in the Aladin Lite API
  const raDec = model.get("_target").split(" ");
  aladin.gotoRaDec(raDec[0], raDec[1]);

  // Set current FoV and WCS
  const twoAxisFoV = { ...aladin.getFov() };
  model.set("_fov_xy", {
    x: twoAxisFoV[0],
    y: twoAxisFoV[1],
  });
  const wcs = { ...aladin.getViewWCS() };
  model.set("_wcs", wcs);
  model.set("_is_loaded", true);
  model.save_changes();

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

  return () => {
    // Need to unsubscribe the listeners
    eventHandler.unsubscribeAll();
  };
}

export default { initialize, render };
