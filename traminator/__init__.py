from octoprint.plugin import TemplatePlugin, StartupPlugin, SimpleApiPlugin, AssetPlugin
from .features.probeplus import ProbeAssistantPlus
from .features.ublmesh import UblMeshGenerator
from collections import ChainMap


class TraminatorPlugin(TemplatePlugin, StartupPlugin, SimpleApiPlugin, AssetPlugin):
    def __init__(self, feature_builders):
        super().__init__()

        self._feature_builders = feature_builders

    def initialize(self):

        # Closure to enforce message identifier usage and simplify sending messages for features
        def send_plugin_message(data):
            self._plugin_manager.send_plugin_message(self._identifier, data)

        self._features = [
            f(self._printer, send_plugin_message, self._logger)
            for f in self._feature_builders
        ]

    def get_assets(self):
        return {"js": ["js/traminator.js"]}

    def get_template_configs(self):
        return [dict(type="tab", template="traminator_tab.jinja2")]

    def get_api_commands(self):
        # Combine all api commands from the features
        return dict(ChainMap(*[f.get_api_commands() for f in self._features]))

    def on_after_startup(self):
        self._logger.debug(
            f"Traminator: {self._identifier}, {self._basefolder}, {self.get_template_configs()}"
        )

    def on_api_command(self, command, data):
        if not self._printer.is_ready():
            return

        [f.on_api_command(command, data) for f in self._features]

    def on_gcode_received(self, comm, line, *args, **kwargs):
        [f.on_gcode_received(self, line) for f in self._features]

        return line


# Inject feature construstors into the plugin. These can be mocked for testing or decorated for extending functionality
traminator = TraminatorPlugin([ProbeAssistantPlus, UblMeshGenerator])

__plugin_name__ = "Traminator"
__plugin_version__ = "1.0.0"
__plugin_description__ = "UI focused on making traming easy"
__plugin_pythoncompat__ = ">=3.7,<4"
__plugin_implementation__ = traminator
__plugin_hooks__ = {
    "octoprint.comm.protocol.gcode.received": traminator.on_gcode_received
}


# Send: G35
# Recv: echo:Active Extruder: 0
# Recv: echo:Active Extruder: 0
# [...]
# Recv: echo:Active Extruder: 0
# [...]
# Recv: Turn Front-Right CCW by 0 turns and 9 minutes (0.08mm)
# Recv: Turn Back-Right CCW by 0 turns and 11 minutes (0.10mm)
# Recv: Turn Back-Left CCW by 0 turns and 1 minutes (0.01mm)


# Bed X: 151.00 Y: 151.00 Z: 0.06


# 240mm screw spacing
# 310mm total width
# 70mm diff therefore 35mm

# G30 X35 Y30
# G30 X275 Y30
# G30 X275 Y270
# G30 X35 Y270
