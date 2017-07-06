import ipywidgets as widgets
from traitlets import Unicode


class Aladin(widgets.DOMWidget):
    _view_name = Unicode('ViewAladin').tag(sync=True)
    _view_module = Unicode('jupyter-widget-ipyaladin').tag(sync=True)
