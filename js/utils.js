/**
 * Converts a string from camelCase to snake_case.
 * @param {string} snakeCaseStr - The string to convert.
 * @returns {string} The string converted to snake_case.
 */
function snakeCaseToCamelCase(snakeCaseStr) {
  if (snakeCaseStr.charAt(0) === "_") snakeCaseStr = snakeCaseStr.slice(1);
  let temp = snakeCaseStr.split("_");
  for (let i = 1; i < temp.length; i++)
    temp[i] = temp[i].charAt(0).toUpperCase() + temp[i].slice(1);
  return temp.join("");
}

/**
 * Converts option names in an object from snake_case to camelCase.
 * @param {Object} options - The options object with snake_case property names.
 * @returns {Object} An object with property names converted to camelCase.
 */
function convertOptionNamesToCamelCase(options) {
  const newOptions = {};
  for (const optionName in options)
    newOptions[snakeCaseToCamelCase(optionName)] = options[optionName];
  return newOptions;
}

class Lock {
  locked = false;

  /**
   * Unlocks the object
   */
  unlock() {
    this.locked = false;
  }

  /**
   * Locks the object
   */
  lock() {
    this.locked = true;
  }
}

let divNumber = -1;
function setDivNumber(num) {
  divNumber = num;
}

function setDivHeight(height, div) {
  if (height == -1) {
    div.style.height = "100%";
  } else {
    div.style.height = `${height}px`;
  }
}

// This is needed to know whether ipyaladin is run
// from a live session or from a static export (HTML)
// Depending on that, we will listen to specific overlay traitlets.
// See the overlays and _overlay_patch traitlets definition for more informations.
function isLiveSession(model) {
  // ipywidgets v7/v8: model.comm is a Comm in live sessions, null/undefined in static HTML
  if (model && model.comm && typeof model.comm.send === "function") return true;

  // Extra heuristics if needed (some frontends expose a kernel on the manager)
  const mgr = model?.widget_manager;
  if (mgr?.kernel) return true; // classic jupyter notebook
  if (mgr?.context?.sessionContext?.session?.kernel) return true; // JupyterLab

  return false; // static export (HTML)
}

export {
  snakeCaseToCamelCase,
  convertOptionNamesToCamelCase,
  Lock,
  divNumber,
  setDivNumber,
  setDivHeight,
  isLiveSession,
};
