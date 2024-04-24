import A from "https://esm.sh/aladin-lite@3.4.0-beta";
import "./widget.css";
import EventHandler from "./models/event_handler";
import { camelCaseToSnakeCase } from "./utils";

let idxView = 0;

function initAladinLite(model, el) {
  let initOptions = {};
  model.get("init_options").forEach((option_name) => {
    initOptions[camelCaseToSnakeCase(option_name)] = model.get(option_name);
  });

  let aladinDiv = document.createElement("div");
  aladinDiv.classList.add("aladin-widget");
  aladinDiv.style.height = `${initOptions["height"]}px`;

  aladinDiv.id = `aladin-lite-div-${idxView}`;
  let aladin = new A.aladin(aladinDiv, initOptions);
  idxView += 1;

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

  const eventHandler = new EventHandler(A, aladin, aladinDiv, model);
  eventHandler.subscribeAll();

  return () => {
    // need to unsubscribe the listeners
    eventHandler.unsubscribeAll();
  };
}

export default { initialize, render };
