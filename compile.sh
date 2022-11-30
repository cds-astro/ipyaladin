#!/bin/sh

npm install yarn
cd js
npm install
cd ..
pip install -e .
jupyter nbextension install --py --symlink --overwrite --sys-prefix ipyaladin
jupyter nbextension enable --py --sys-prefix ipyaladin
jupyter labextension develop ipyaladin --overwrite