from ._version import version_info, __version__

from .aladin_widget import *

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'ipyaladin',
        'require': 'ipyaladin/extension'
    }]
