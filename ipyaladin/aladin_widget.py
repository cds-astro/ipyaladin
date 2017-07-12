from ipywidgets import (widgets)
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
    coo_frame = Unicode("J2000").tag(sync=True, o=True) 
    survey = Unicode("P/DSS2/color").tag(sync=True, o=True)

    # the remaining values exists for the widget constructor's sole purpose
    reticle_size = Float(22).tag(sync=True, o=True)
    reticle_color = Unicode("rgb(178, 50, 178)").tag(sync=True, o=True)
    show_reticle = Bool(True).tag(sync=True, o=True)
    show_zoom_control = Bool(True).tag(sync=True, o=True)
    show_fullscreen_control = Bool(True).tag(sync=True, o=True)
    show_layers_control = Bool(True).tag(sync=True, o=True)
    show_goto_control = Bool(True).tag(sync=True, o=True)
    show_share_control = Bool(False).tag(sync=True, o=True)
    show_catalog = Bool(True).tag(sync=True, o=True)
    show_frame = Bool(True).tag(sync=True, o=True)
    show_coo_grid = Bool(False).tag(sync=True, o=True)
    full_screen = Bool(False).tag(sync=True, o=True)
    log = Bool(True).tag(sync=True, o=True)
    allow_full_zoomout = Bool(False).tag(sync=True, o=True)

    options = List(trait=Unicode).tag(sync=True)

    # the following values are used in the classe's functions

    # values used in the add_catalogFromUrl function
    votable_URL = Unicode('').tag(sync=True)
    votable_options = Dict().tag(sync=True)
    votable_from_URL_flag = Bool(True).tag(sync=True)

    # values used in the add_table function
    table_keys = List().tag(sync=True)
    table_columns = List().tag(sync=True)
    table_flag = Bool(True).tag(sync=True)

    # values used in the add_listener function
    listener_type = Unicode('').tag(sync=True)
    listener_flag = Bool(True).tag(sync=True)

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
        # trigger the handle_aladin_event function when the send function is called on the js-side
        self.on_msg(self.handle_aladin_event)

    # Note: (about the classe's functions)
    # As it is only possible to communicate with the js side of the application by using traitlets,
    # we can not directly call a js function from the python side
    # As such, we use a little trick that consists in delegating to one of the class's variable
    # the role of a flag, whose change in value trigger a listener in the js side,
    # who can then execute the function whose parameters are passed as trailets in its python equivalent

    def add_catalog_from_URL(self, votable_URL, votable_options):
        ''' load a VOTable table from an url and load its data into the widget 
            Args:
                votable_URL: string url
                votable_options: dictionary object'''
        self.votable_URL= votable_URL
        self.votable_options= votable_options
        self.votable_from_URL_flag= not self.votable_from_URL_flag

    # Notes:
    # 1 - The loaded table can possess fields tagged as 'masked', who can not be parsed by JSON
    #     As such, the table's columns cant be obtained through the use of table.columns,
    #     and the use of table.__array__() is requiered.
    # 2 - It seems that the list.append() method does not work with traitlets,
    #     the affectation of the columns must be done at once by using a buffer.
    def add_table(self, table):
        ''' load a VOTable -already accessible on the python side- into the widget
            Args:
                table: votable object'''
        table_array = table.__array__()
        self.table_keys= table.keys()
        table_columns= []
        for i in range(0,len(table.columns[0])):
            table_columns.append(list(table_array[i]));
        self.table_columns = table_columns
        self.table_flag= not self.table_flag

    def add_listener(self, listener_type):
        ''' add a listener to the widget
            Args:
                listener_type: string that can either be 'objectHovered' or 'objClicked' '''
        self.listener_type= listener_type
        self.listener_flag= not self.listener_flag

    # Note: the print() option end='\r' allow us to override the previous prints,
    # thus only the last message will be displayed at the screen
    def handle_aladin_event(self, _, content, buffers):
        ''' used to collect json objects that are sent by the js-side of the application by using the send() method '''
        if content.get('event', '').startswith('print'):
            print(content.get('message'), end='\r')