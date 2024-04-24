import A from "https://esm.sh/aladin-lite@3.4.0-beta";
import "./widget.css";
import EventHandler from "./models/event_handler";

let idxView = 0;

function camelCaseToSnakeCase(pyname) {
  if (pyname.charAt(0) === "_") pyname = pyname.slice(1);
  let temp = pyname.split("_");
  for (let i = 1; i < temp.length; i++) {
    temp[i] = temp[i].charAt(0).toUpperCase() + temp[i].slice(1);
  }
  return temp.join("");
}

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
