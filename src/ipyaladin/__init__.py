import importlib.metadata
import math
import pathlib
import warnings

import anywidget
from traitlets import (Float, Int, Unicode, Bool, List, Dict, Any, Bytes, default, Undefined)

try:
    __version__ = importlib.metadata.version("ipyaladin")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

class Aladin(anywidget.AnyWidget):

    _esm = pathlib.Path(__file__).parent / "static" / "widget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"

    # Options for the view initialization
    height = Int(400).tag(sync=True, init_option=True)
    target = Unicode("0 0").tag(sync=True, init_option=True)
    fov = Float(60.0).tag(sync=True, init_option=True)
    survey = Unicode("https://alaskybis.unistra.fr/DSS/DSSColor").tag(sync=True, init_option=True)
    coo_frame = Unicode("J2000").tag(sync=True, init_option=True)
    projection = Unicode("SIN").tag(sync=True, init_option=True)
    samp = Bool(False).tag(sync=True, init_option=True)
    # Buttons on/off
    background_color = Unicode("rgb(60, 60, 60)").tag(sync=True, init_option=True)
    show_zoom_control = Bool(False).tag(sync=True, init_option=True)
    show_layers_control = Bool(True).tag(sync=True, init_option=True)
    show_overlay_stack_control = Bool(True).tag(sync=True, init_option=True)
    show_fullscreen_control = Bool(True).tag(sync=True, init_option=True)
    show_simbad_pointer_control = Bool(True).tag(sync=True, init_option=True)
    show_settings_control = Bool(True).tag(sync=True, init_option=True)
    show_share_control = Bool(False).tag(sync=True, init_option=True)
    show_status_bar = Bool(True).tag(sync=True, init_option=True)
    show_frame = Bool(True).tag(sync=True, init_option=True)
    show_fov = Bool(True).tag(sync=True, init_option=True)
    show_coo_location = Bool(True).tag(sync=True, init_option=True)
    show_projection_control = Bool(True).tag(sync=True, init_option=True)
    show_context_menu = Bool(True).tag(sync=True, init_option=True)
    show_catalog = Bool(True).tag(sync=True, init_option=True)
    full_screen = Bool(False).tag(sync=True, init_option=True)
    # reticle
    show_reticle = Bool(True).tag(sync=True, init_option=True)
    reticle_color = Unicode("rgb(178, 50, 178)").tag(sync=True, init_option=True)
    reticle_size = Int(20).tag(sync=True, init_option=True)
    # grid
    show_coo_grid = Bool(False).tag(sync=True, init_option=True)
    show_coo_grid_control = Bool(True).tag(sync=True, init_option=True)
    grid_color = Unicode("rgb(178, 50, 178)").tag(sync=True, init_option=True)
    grid_opacity = Float(0.5).tag(sync=True, init_option=True)
    grid_options = Dict().tag(sync=True, init_option=True) # TODO: test once aladin 3.3.0 is out

    # content of the last click
    clicked = Dict().tag(sync=True)
    # listener callback is only on the python side and contains functions to link to events
    listener_callback = {}

    # overlay survey
    overlay_survey = Unicode('').tag(sync=True, init_option=True)
    overlay_survey_opacity = Float(0.0).tag(sync=True, init_option=True)

    # tables/catalogs
    _table = Bytes(Undefined).tag(sync=True)
    

    init_options = List(trait=Any()).tag(sync=True)
    @default("init_options")
    def _init_options(self):
        return [name for name in self.traits(init_option=True)]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_msg(self._handle_custom_message)
    
    def __dir__(self):
        return [
            "add_moc",
            "add_overlay_from_stcs",
            "add_catalog_from_URL",
            "add_listener",
        ]
    
    def _handle_custom_message(self, model, message, list_of_buffers):
        event_type = message["event_type"]
        message_content = message["content"]
        if event_type == "object_clicked" and "object_clicked" in self.listener_callback:
            self.listener_callback["object_clicked"](message_content)
        elif event_type == "object_hovered" and "object_hovered" in self.listener_callback:
            self.listener_callback["object_hovered"](message_content)
        elif event_type == "click" and "click" in self.listener_callback:
            self.listener_callback["click"](message_content)
    
    # Note: (about the class's functions)
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
        self.send({
            "event_name": "add_catalog_from_URL",
            "votable_URL": votable_URL,
            "options": votable_options
        })

    # MOCs
    
    def add_moc(self, moc, **moc_options):
        if isinstance(moc, dict):
            self.send({
                "event_name": "add_MOC_from_dict",
                "moc_dict": moc,
                "options": moc_options
            })
        elif isinstance(moc, str) and "://" in moc:
            self.send({
                "event_name": "add_MOC_from_URL",
                "moc_URL": moc,
                "options": moc_options
            })
        else:
            try:
                from mocpy import MOC
                if isinstance(moc, MOC):
                    self.send({
                        "event_name": "add_MOC_from_dict",
                        "moc_dict": moc.serialize("json"),
                        "options": moc_options
                    })
            except ImportError:
                raise ValueError("A MOC can be given as an URL, a dictionnary, or a mocpy.MOC object. "
                                 "To read mocpy.MOC objects, you need to install the mocpy library with "
                                 "'pip install mocpy'.")


    def add_moc_from_URL(self, moc_URL, moc_options = {}):
        """ load a MOC from a URL and display it in Aladin Lite widget
            Arguments:
            moc_URL: string url
            moc_options: dictionary object"""
        warnings.warn("add_moc_from_URL is replaced by add_moc that detects automatically"
                      "that the MOC was given as an URL.", DeprecationWarning)
        self.add_moc(moc_URL, **moc_options)


    def add_moc_from_dict(self, moc_dict, moc_options = {}):
        """ load a MOC from a dict object and display it in Aladin Lite widget
            Arguments:
            moc_dict: the dict containing the MOC cells. Key are the HEALPix orders,
                      values are the pixel indexes, eg: {"1":[1,2,4], "2":[12,13,14,21,23,25]} 
            moc_options: dictionary object"""
        warnings.warn("add_moc_from_dict is replaced by add_moc that detects automatically"
                      "that the MOC was given as a dictionary.", DeprecationWarning)
        self.add_moc(moc_dict, **moc_options)


    # Notes:
    # 1 - The loaded table can possess fields tagged as 'masked', who can not be parsed by JSON
    #     As such, the table's columns cant be obtained through the use of table.columns,
    #     and the use of table.__array__() is requiered.
    # 2 - It seems that the list.append() method does not work with traitlets,
    #     the affectation of the columns must be done at once by using a buffer.
    def add_table(self, table, **table_options):
        """ Load a table into the widget.

        Parameters
        ----------
        table : astropy.table.table.QTable or astropy.table.table.Table
                table that must contain coordinates information
        
        Examples
        --------
        Cell 1:
        >>> from ipyaladin import Aladin
        >>> from astropy.table import QTable
        >>> aladin = Aladin(fov=2, target='M1')
        >>> aladin
        Cell 2:
        >>> ra = [83.63451584700, 83.61368056017, 83.58780251600]
        >>> dec = [22.05652591227, 21.97517807639, 21.99277764451]
        >>> name = ["Gaia EDR3 3403818589184411648",
                    "Gaia EDR3 3403817661471500416",
                    "Gaia EDR3 3403817936349408000",
                   ]
        >>> table = QTable([ra, dec, name],
                            names=("ra", "dec", "name"),
                            meta={"name": "my sample table"})
        >>> aladin.add_table(table)
        And the table should appear in the output of Cell 1!
        """

        # this library must be installed, and is used in votable operations
        # http://www.astropy.org/
        import astropy
        import io

        table_bytes = io.BytesIO()
        table.write(table_bytes, format="votable")
        self._table = table_bytes.getvalue()
        self.send({
            "event_name": "add_table",
            "options": table_options
        })


        

    def add_overlay_from_stcs(self, stc_string, **overlay_options):
        """ Add an overlay layer defined by a STC-S string

            Args:
                stc_string: the STC-S string. Can be on multiple lines, delimited by \n separators
                overlay_options: the STC-S string. Can be on multiple lines, delimited by \n separators"""
        self.send({
            "event_name": "add_overlay_from_stcs",
            "stc_string": stc_string,
            "overlay_options": overlay_options
        })

    # Note: the print() options end='\r'allow us to override the previous prints,
    # thus only the last message will be displayed at the screen

    def get_JPEG_thumbnail(self):
        """ create a popup window that contains an image representing the widget's current state """
        self.send({
            "event_name": "get_JPG_thumbnail"
        })

    def set_color_map(self, color_map_name):
        self.send({
            "event_name": "change_colormap",
            "colormap": color_map_name
        })

    def rectangular_selection(self):
        self.send({
            "event_name": "trigger_rectangular_selection"
        })

    # Adding a listener
        
    def add_listener(self, listener_type, callback):
        """ add a listener to the widget
            Args:
                listener_type: string that can either be 'objectHovered' or 'objClicked' 
                callback: python function"""
        if listener_type == 'objectHovered' or listener_type == "object_hovered":
            self.listener_callback["object_hovered"] =  callback
        elif listener_type == 'objectClicked' or listener_type == "object_clicked":
            self.listener_callback["object_clicked"] = callback
        elif listener_type == 'click':
            self.listener_callback["click"] = callback
        elif listener_type == 'select':
            self.listener_callback["select"] = callback