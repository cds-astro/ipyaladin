import ipywidgets as widgets
from traitlets import (Float, Unicode, Bool, List, Dict, default)

# theses library must be installed, and are used in votable operations
# https://astroquery.readthedocs.io/en/latest/
# http://www.astropy.org/
from astroquery.simbad import Simbad
import astropy

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

    # the following values are used in the classe's functions

    # values used in the addCatalogFromUrl function
    votableURL = Unicode('').tag(sync=True)
    votableOptions = Dict().tag(sync=True)
    votableFromURLFlag = Bool(True).tag(sync=True)

    # values used in the addTable function
    tableKeys = List().tag(sync=True)
    tableColumns = List([[1,2],[3,4]]).tag(sync=True)
    tableFlag = Bool(True).tag(sync=True)

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

    # Note: (about the classe's functions)
    # As it is only possible to communicate with the js side of the application by using traitlets,
    # we can not directly call a js function from the python side
    # As such, we use a little trick that consists in delegating to one of the class's variable
    # the role of a flag, whose change in value trigger a listener in the js side,
    # who can then execute the function whose parameters are passed as trailets in its python equivalent

    def addCatalogFromURL(self, votableURL, votableOptions):
        ''' load a VOTable table from an url and load its data into the widget '''
        self.votableURL= votableURL
        self.votableOptions= votableOptions
        self.votableFlag= not self.votableFromURLFlag

    # Notes:
    # 1 - The loaded table can possess fields tagged as 'masked', who can not be parsed by JSON
    #     As such, the table's columns cant be obtained through the use of table.columns,
    #     and the use of table.__array__() is requiered.
    # 2 - It seems that the list.append() method does not work with traitlets,
    #     the affectation of the columns must be done at once by using a buffer.
    def addTable(self, table):
        ''' load a VOTable -already accessible on the python side- into the widget '''
        table_array = table.__array__()
        self.tableKeys= table.keys()
        tableColumns= []
        for i in range(0,len(table.columns[0])):
            tableColumns.append(list(table_array[i]));
        self.tableColumns = tableColumns
        self.tableFlag= not self.tableFlag