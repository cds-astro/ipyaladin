import "./widget.css";
import EventHandler from "./models/event_handler";
import { snakeCaseToCamelCase } from "./utils";
import A from "./imports";

let idxView = 0;

function initAladinLite(model, el) {
  let initOptions = {};
  model.get("init_options").forEach((option_name) => {
    initOptions[snakeCaseToCamelCase(option_name)] = model.get(option_name);
  });

  let aladinDiv = document.createElement("div");
  aladinDiv.classList.add("aladin-widget");
  aladinDiv.style.height = `${initOptions["height"]}px`;

  aladinDiv.id = `aladin-lite-div-${idxView}`;
  let aladin = new A.aladin(aladinDiv, initOptions);
  idxView += 1;

  // Set the target again after the initialization to be sure that the target is set
  // from icrs coordinates because of the use of gotoObject in the Aladin Lite API
  const raDec = initOptions["target"].split(" ");
  aladin.gotoRaDec(raDec[0], raDec[1]);

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
