@echo off

Rem Activate ipyaladin for simple notebooks
"%PREFIX%\Scripts\jupyter-nbextension.exe" enable --py widgetsnbextension > NUL 2>&1 && if errorlevel 1 exit 1
"%PREFIX%\Scripts\jupyter-nbextension.exe" enable ipyaladin --py --sys-prefix > NUL 2>&1 && if errorlevel 1 exit 1
Rem Activate ipyaladin extension for jupyter lab (todo, currently it does not work)
Rem "%PREFIX%\Scripts\jupyter-labextension.exe" develop ipyaladin --overwrite > NUL 2>&1 && if errorlevel 1 exit 1