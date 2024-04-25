import A from "https://esm.sh/aladin-lite@3.3.3-beta";

function camelCaseToSnakeCase(pyname) {
  if (pyname.charAt(0) === "_") pyname = pyname.slice(1);
  let temp = pyname.split("_");
  for (let i = 1; i < temp.length; i++) {
    temp[i] = temp[i].charAt(0).toUpperCase() + temp[i].slice(1);
  }
  return temp.join("");
}

export { camelCaseToSnakeCase, A };
