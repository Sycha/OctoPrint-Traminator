import re


class ProbeAssistantPlus:
    CMD_PROBE = "probe"
    CMD_WIZARD = "wizard"
    SCREWMMPERTURN = {"M3": 0.5}

    def __init__(self, printer, send_plugin_messsage, logger):
        self._printer = printer
        self._send_plugin_message = send_plugin_messsage
        self._logger = logger
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
        self._origin_offset = 0

    def get_api_commands(self):
        return {self.CMD_PROBE: [], self.CMD_WIZARD: []}

    def on_api_command(self, command, data):
        if command == self.CMD_PROBE:
            self._logger.info(f"Running probe{data}")
            location = data["location"]
            coords = self._probe_locations[location]
            self.run_probe(coords[0], coords[1])

        if command == self.CMD_WIZARD:
            self._logger.info("Running probe wizard")
            for p in self._probe_locations:
                self.run_probe(p[0], p[1])

    def on_gcode_received(self, comm, line, *args, **kwargs):
        self.try_parse_probe_result(line)
        return line

    @property
    def origin(self):
        return self._probe_samples[0]

    def run_probe(self, x, y):
        self._printer.commands(["G28 O", f"G30 X{x} Y{y}"])

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
            minutes = int(round(float(abs(z)) / self.SCREWMMPERTURN["M3"] * 60))
            turns = minutes // 60
            minutes = minutes - (turns * 60)

            advice = f"{direction} {turns} turns and {minutes} minutes"

        # Send to web frontend
        self._send_plugin_message(
            {
                "type": "probe",
                "location": location,
                "z": z,
                "advice": advice,
            },
        )
