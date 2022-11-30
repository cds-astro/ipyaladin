# Activate ipyaladin for simple notebooks
"${PREFIX}/bin/jupyter-nbextension" enable --py widgetsnbextension
"${PREFIX}/bin/jupyter-nbextension" enable --py --sys-prefix ipyaladin
# Activate ipyaladin extension for jupyter lab (todo, currently it does not work)
# "${PREFIX}/bin/jupyter-labextension" develop ipyaladin --overwrite