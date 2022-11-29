# Activate ipyaladin for simple notebooks
"${PREFIX}/bin/jupyter-nbextension" --py --symlink --overwrite --sys-prefix ipyaladin
"${PREFIX}/bin/jupyter-nbextension" enable --py --sys-prefix ipyaladin
# Activate ipyaladin extension for jupyter lab
"${PREFIX}/bin/jupyter-labextension" develop ipyaladin --overwrite