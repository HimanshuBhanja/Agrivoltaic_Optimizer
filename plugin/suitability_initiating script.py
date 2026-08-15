import sys
if 'agrivoltaic_plugin' in sys.modules:
    del sys.modules['agrivoltaic_plugin']

sys.path.append(
    r'D:\Msc Agri. Analytics\2nd Sem\Assignments\ML Assignment\Agrivoltaic_Optimizer\plugin'
)

import importlib
import agrivoltaic_plugin
importlib.reload(agrivoltaic_plugin)

agrivoltaic_plugin.launch_panel(iface)