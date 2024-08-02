import "./widget.css";
import EventHandler from "./models/event_handler";
import { divNumber, setDivNumber, snakeCaseToCamelCase } from "./utils";
import A from "./aladin_lite";

function initAladinLite(model, el) {
  setDivNumber(divNumber + 1);
  let initOptions = {};
  model.get("init_options").forEach((option_name) => {
    initOptions[snakeCaseToCamelCase(option_name)] = model.get(option_name);
  });

  let aladinDiv = document.createElement("div");
  aladinDiv.classList.add("aladin-widget");
  aladinDiv.style.height = `${initOptions["height"]}px`;

  aladinDiv.id = `aladin-lite-div-${divNumber}`;
  let aladin = new A.aladin(aladinDiv, initOptions);

  // Set the target again after the initialization to be sure that the target is set
  // from icrs coordinates because of the use of gotoObject in the Aladin Lite API
  const raDec = initOptions["target"].split(" ");
  aladin.gotoRaDec(raDec[0], raDec[1]);

  // Set current FoV and WCS
  const twoAxisFoV = aladin.getFov();
  model.set("_fov_xy", {
    x: twoAxisFoV[0],
    y: twoAxisFoV[1],
  });
  model.set("_wcs", aladin.getViewWCS());
  model.set("_ready", true);
  model.save_changes();

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

  return () => {
    // Need to unsubscribe the listeners
    eventHandler.unsubscribeAll();
  };
}

export default { initialize, render };
