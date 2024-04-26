import A from "https://esm.sh/aladin-lite@3.3.3-beta";

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

export { snakeCaseToCamelCase, convertOptionNamesToCamelCase, A };
