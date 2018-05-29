from ipywidgets import (widgets)
from ipywidgets import widget_serialization
from traitlets import (Float, Unicode, Bool, List, Dict, default)
import logging

logger = logging.getLogger('aladin_widget.py')



""" Definition of the AladinLite widget in the python kernel """
class Aladin(widgets.DOMWidget):
    _view_name = Unicode('ViewAladin').tag(sync=True)
    _model_name = Unicode('ModelAladin').tag(sync=True)
    _view_module = Unicode('ipyaladin').tag(sync=True)
    _model_module = Unicode('ipyaladin').tag(sync=True)
    _view_module_version = Unicode('0.1.3').tag(sync=True)
    _model_module_version = Unicode('0.1.3').tag(sync=True)


    # Aladin options must be declared here (as python class's attributes), 
    # so that they can be synchronized from the python side to the javascript side
    # Default values are overwritten by values passed to the class's constructor
    
    # only theses 4 values are actually updated on one side when they change on the other
    fov = Float(60).tag(sync=True, o=True)
    target = Unicode("0 +0").tag(sync=True, o=True)
    coo_frame = Unicode("J2000").tag(sync=True, o=True) 
    survey = Unicode("P/DSS2/color").tag(sync=True, o=True)
    overlay_survey = Unicode('').tag(sync=True, o=True)
    overlay_survey_opacity = Float(0.0).tag(sync=True, o=True)

    # values used in selection
    selection_ids = List(allow_none=True, default_value=None).tag(sync=True, o=True, **widget_serialization)
#    selection_ids = List(trait=Unicode).tag(sync=True)
#    selection_ids_flag = Bool(True).tag(sync=True)
#    selection_test = Bool(False).tag(sync=True)
#    selectionnumber = Float(0.0).tag(sync=True, o=True)
    
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

    # values used in the add_catalog_from_URL function
    votable_URL = Unicode('').tag(sync=True)
    votable_options = Dict().tag(sync=True)
    votable_from_URL_flag = Bool(True).tag(sync=True)

    # values used in the add_moc_from_URL function
    moc_URL = Unicode('').tag(sync=True)
    moc_options = Dict().tag(sync=True)
    moc_from_URL_flag = Bool(True).tag(sync=True)

    # values used in the add_moc_from_dict function
    moc_dict = Dict().tag(sync=True)
    moc_from_dict_flag = Bool(True).tag(sync=True)

    # values used in the add_table function
    table_keys = List().tag(sync=True)
    table_columns = List().tag(sync=True)
    table_flag = Bool(True).tag(sync=True)

    # values used in the add_listener function
    listener_type = Unicode('').tag(sync=True)
    listener_flag = Bool(True).tag(sync=True)
    listener_callback_source_click = None
    listener_callback_source_hover = None
    listener_callback_click = None

    last_prompt_length = 0

    # values used in the get_JPEG_thumbnail function
    thumbnail_flag = Bool(True).tag(sync=True)

    # 
    color_map_name = Unicode('').tag(sync=True)
    color_map_flag = Bool(True).tag(sync=True)

    @default('options')
    def _default_options(self):
        """ fill the options List with all the options declared """
        return [name for name in self.traits(o=True)]

    def __init__(self, **kwargs):
        """ class constructor
            Args:
                kwargs: widget options
        """
        super(Aladin, self).__init__(**kwargs)
        if kwargs.get('selection_update'):
            self.selection_update = kwargs.get('selection_update')
        # trigger the handle_aladin_event function when the send function is called on the js-side
        # see: http://jupyter-notebook.readthedocs.io/en/latest/comms.html
        self.on_msg(self.handle_aladin_event)

    # Note: (about the classe's functions)
    # As it is only possible to communicate with the js side of the application by using traitlets,
    # we can not directly call a js function from the python side
    # As such, we use a little trick that consists in delegating to one of the class's variable
    # the role of a flag, whose change in value trigger a listener in the js side,
    # who can then execute the function whose parameters are passed as trailets in its python equivalent

    def add_catalog_from_URL(self, votable_URL, votable_options={}):
        """ load a VOTable table from an url and load its data into the widget 
            Args:
                votable_URL: string url
                votable_options: dictionary object"""
        self.votable_URL= votable_URL
        self.votable_options= votable_options
        self.votable_from_URL_flag= not self.votable_from_URL_flag

    def add_moc_from_URL(self, moc_URL, moc_options = {}):
        """ load a MOC from a URL and display it in Aladin Lite widget
            Arguments:
            moc_URL: string url
            moc_options: dictionary object"""
        self.moc_URL = moc_URL
        self.moc_options = moc_options
        self.moc_from_URL_flag = not self.moc_from_URL_flag

    def add_moc_from_dict(self, moc_dict, moc_options = {}):
        """ load a MOC from a dict object and display it in Aladin Lite widget
            Arguments:
            moc_dict: the dict containing the MOC cells. Key are the HEALPix orders,
                      values are the pixel indexes, eg: {"1":[1,2,4], "2":[12,13,14,21,23,25]} 
            moc_options: dictionary object"""
        self.moc_dict = moc_dict
        self.moc_options = moc_options
        self.moc_from_dict_flag = not self.moc_from_dict_flag

    # Notes:
    # 1 - The loaded table can possess fields tagged as 'masked', who can not be parsed by JSON
    #     As such, the table's columns cant be obtained through the use of table.columns,
    #     and the use of table.__array__() is requiered.
    # 2 - It seems that the list.append() method does not work with traitlets,
    #     the affectation of the columns must be done at once by using a buffer.
    def add_table(self, table):
        """ load a VOTable -already accessible on the python side- into the widget
            Args:
                table: votable object"""

        # theses library must be installed, and are used in votable operations
        # http://www.astropy.org/
        import astropy
        import numpy as np

        table_array = table.__array__()
        self.table_keys= table.keys()
        table_columns= []
        for i in range(0,len(table.columns[0])):
            row_data = []

            # this step is needed in order to properly retrieve strings data
            # (otherwise, Aladin Lite shows these values as DataView object)
            for item in table_array[i]:
                if isinstance(item, bytes):
                    row_data.append(item.decode('utf-8'))
                elif isinstance(item, np.int64):
                    row_data.append(str(item))
                else:
                    row_data.append(item)
            table_columns.append(row_data)

        self.table_columns = table_columns
        self.table_flag= not self.table_flag

    def add_listener(self, listener_type, callback):
        """ add a listener to the widget
            Args:
                listener_type: string that can either be 'objectHovered' or 'objClicked' 
                callback: python function"""
        self.listener_type= listener_type
        if listener_type == 'objectHovered':
            self.listener_callback_source_hover= callback
        elif listener_type == 'objectClicked':
            self.listener_callback_source_click= callback
        elif listener_type == 'click':
            self.listener_callback_click= callback

        self.listener_flag= not self.listener_flag

    # Note: the print() options end='\r'allow us to override the previous prints,
    # thus only the last message will be displayed at the screen
    def handle_aladin_event(self, _, content, buffers):
        """ used to collect json objects that are sent by the js-side of the application by using the send() method """
        if content.get('event', '').startswith('callback'):
            if content.get('type') == 'objectHovered':
                result= self.listener_callback_source_hover(content.get('data'))
            elif content.get('type') == 'objectClicked':
                result= self.listener_callback_source_click(content.get('data'))
            elif content.get('type') == 'click':
                result= self.listener_callback_click(content.get('data'))
            result= str(result)
            for i in  range(len(result),self.last_prompt_length):
                result= result+' '
            print(result, end='\r')
            self.last_prompt_length= len(result)
        else:
            if (content.get('event', '').startswith('selection')
                and self.selection_update):
                self.selection_ids = content.get('ids')
                self.selection_update(self.selection_ids)
            
    def get_JPEG_thumbnail(self):
        """ create a popup window that contains an image representing the widget's current state """
        self.thumbnail_flag= not self.thumbnail_flag

    def set_color_map(self, color_map_name):
        self.color_map_name= color_map_name
        self.color_map_flag= not self.color_map_flag
