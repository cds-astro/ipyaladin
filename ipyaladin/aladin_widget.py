import ipywidgets as widgets
from traitlets import (Float, Unicode, List, default)

class InteractMixin(object):

    def interact(self, **kwargs):
        c = []
        for name, abbrev in kwargs.items():
            default = getattr(self, name)
            widget = interactive.widget_from_abbrev(abbrev, default)
            if not widget.description:
                widget.description = name
            widget.link = link((widget, 'value'), (self, name))
            c.append(widget)
        cont = Box(children=c)
        return cont

class Aladin(widgets.DOMWidget, InteractMixin):
    _view_name = Unicode('ViewAladin').tag(sync=True)
    _model_name = Unicode('ModelAladin').tag(sync=True)
    _view_module = Unicode('jupyter-widget-ipyaladin').tag(sync=True)
    _model_module = Unicode('jupyter-widget-ipyaladin').tag(sync=True)

    fov = Float(1).tag(sync=True, o=True)
    target = Unicode("messier 104").tag(sync=True, o=True)

    options = List(trait=Unicode).tag(sync=True)

    @default('options')
    def _default_options(self):
        return [name for name in self.traits(o=True)]

    def __init__(self, **kwargs):
        super(Aladin, self).__init__(**kwargs)

    
