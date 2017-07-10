import ipywidgets as widgets
from traitlets import (Float, Unicode, Bool, List, default)

''' Definition of the AladinLite widget in the python kernel '''
class Aladin(widgets.DOMWidget):
    _view_name = Unicode('ViewAladin').tag(sync=True)
    _model_name = Unicode('ModelAladin').tag(sync=True)
    _view_module = Unicode('jupyter-widget-ipyaladin').tag(sync=True)
    _model_module = Unicode('jupyter-widget-ipyaladin').tag(sync=True)

    # Aladin options must be declared here (as python class's attributes), 
    # so that they can be synchronized from the python side to the javascript side
    # Default values are overwritten by values passed to the class's constructor
    
    # only theses 4 values are actually updated on one side when they change on the other
    fov = Float(60).tag(sync=True, o=True)
    target = Unicode("0 +0").tag(sync=True, o=True)
    cooFrame = Unicode("J2000").tag(sync=True, o=True) 
    survey = Unicode("P/DSS2/color").tag(sync=True, o=True)

    # the remaining values exists for the widget constructor's sole purpose
    reticleSize = Float(22).tag(sync=True, o=True)
    reticleColor = Unicode("rgb(178, 50, 178)").tag(sync=True, o=True)
    showReticle = Bool(True).tag(sync=True, o=True)
    showZoomControl = Bool(True).tag(sync=True, o=True)
    showFullscreenControl = Bool(True).tag(sync=True, o=True)
    showLayersControl = Bool(True).tag(sync=True, o=True)
    showGotoControl = Bool(True).tag(sync=True, o=True)
    showShareControl = Bool(False).tag(sync=True, o=True)
    showCatalog = Bool(True).tag(sync=True, o=True)
    showFrame = Bool(True).tag(sync=True, o=True)
    showCooGrid = Bool(False).tag(sync=True, o=True)
    fullScreen = Bool(False).tag(sync=True, o=True)
    log = Bool(True).tag(sync=True, o=True)
    allowFullZoomout = Bool(False).tag(sync=True, o=True)

    options = List(trait=Unicode).tag(sync=True)

    @default('options')
    def _default_options(self):
        ''' fill the options List with all the options declared '''
        return [name for name in self.traits(o=True)]

    def __init__(self, **kwargs):
        ''' class constructor
            Args:
                kwargs: widget options
        '''
        super(Aladin, self).__init__(**kwargs)

    
