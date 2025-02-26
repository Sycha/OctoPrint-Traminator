from octoprint.plugin import TemplatePlugin, StartupPlugin, SimpleApiPlugin, AssetPlugin
import re
from asyncio import Queue

CMD_PROBE = "probe"
CMD_WIZARD = "wizard"


SCREWMMPERTURN = {"M3": 0.5}


class TraminatorPlugin(TemplatePlugin, StartupPlugin, SimpleApiPlugin, AssetPlugin):
    def __init__(self):
        super().__init__()
        self._probe_pattern = re.compile(
            "^Bed X: ([-0-9.]*) Y: ([-0-9.]*) Z: ([-0-9.]*)$"
        )
        self._probe_locations = [
            (35.0, 30.0),
            (270.0, 30.0),
            (270.0, 270.0),
            (35.0, 270.0),
        ]
        self._probe_samples = {}
        self._task_queue = Queue()
        self._origin_offset = 0

    def get_assets(self):
        return {"js": ["js/traminator.js"]}

    def get_template_configs(self):
        return [dict(type="tab", template="traminator_tab.jinja2")]

    def get_api_commands(self):
        return {CMD_PROBE: [], CMD_WIZARD: []}

    def on_after_startup(self):
        self._logger.debug(
            f"Traminator: {self._identifier}, {self._basefolder}, {self.get_template_configs()}"
        )

    def on_api_command(self, command, data):
        if not self._printer.is_ready():
            return

        if command == CMD_PROBE:
            self._logger.info(f"Running probe{data}")
            location = data["location"]
            coords = self._probe_locations[location]
            self.run_probe(coords[0], coords[1])

        if command == CMD_WIZARD:
            self._logger.info("Running probe wizard")
            for p in self._probe_locations:
                self.run_probe(p[0], p[1])

    def on_gcode_received(self, comm, line, *args, **kwargs):
        self.try_parse_probe_result(line)

        return line

    @property
    def origin(self):
        return self._probe_samples[0]

    def try_parse_probe_result(self, line):
        gcode_match = self._probe_pattern.match(line)
        if gcode_match is None:
            return

        self._logger.info("Received z-probe result")

        # Convert string matches to structured data
        locationCoords = (float(gcode_match.group(1)), float(gcode_match.group(2)))
        z = float(gcode_match.group(3))
        location = self._probe_locations.index(locationCoords)

        self._logger.info(f"{location}: {locationCoords} = {z}")

        # Retain the probe value
        self._probe_samples[location] = z

        # Create human tramming advice
        advice = ""

        # Datum probe
        if location == 0:
            self._logger.info("New Origin")
            if self.origin != z:
                # Reset the samples
                self._probe_samples = {location: z}

            advice = "Datum"

        # Dependant screw probe
        elif location:
            self._logger.info("Normaled on origin")
            z = round(z - self.origin, 2)

            direction = "CW" if z < 0 else "CCW"
            minutes = int(round(float(abs(z)) / SCREWMMPERTURN["M3"] * 60))
            turns = minutes // 60
            minutes = minutes - (turns * 60)

            advice = f"{direction} {turns} turns and {minutes} minutes"

        # Send to web frontend
        self._plugin_manager.send_plugin_message(
            self._identifier,
            {
                "type": "probe",
                "location": location,
                "z": z,
                "advice": advice,
            },
        )

    def run_probe(self, x, y):
        self._printer.commands(["G28 O", f"G30 X{x} Y{y}"])


traminator = TraminatorPlugin()

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
