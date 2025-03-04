import re


class UblMeshGenerator:
    CMD_UBLAUTOPROBE = "ublAutoProbe"
    CMD_UBLFILLUNPOPULATED = "ublFillUnpopulated"

    def __init__(self, printer, send_plugin_message, logger):
        self._printer = printer
        self._send_plugin_message = send_plugin_message
        self._logger = logger
        # Probing mesh point 80/100
        self._meshProbingProgressPattern = re.compile(
            "Probing mesh point ([0-9]*)/([0-9]*)\\."
        )

    def get_api_commands(self):
        return {
            self.CMD_UBLAUTOPROBE: [],
            self.CMD_UBLFILLUNPOPULATED: [],
        }

    def on_api_command(self, command, data):
        if command == self.CMD_UBLAUTOPROBE:
            self._logger.info("Running UBL Auto Probe")
            self.run_ubl_auto_probe()

        if command == self.CMD_UBLFILLUNPOPULATED:
            self._logger.info("Running fill unpopulated")
            self.run_ubl_fill_unpopulated()

    def on_gcode_received(self, comm, line, *args, **kwargs):
        self.try_parse_meshProbingProgress(line)
        return line

    def run_ubl_auto_probe(self):
        self._printer.commands(["G28 O", "G29 P1 T1", "M117 Autoprobe complete"])

    def run_ubl_fill_unpopulated(self):
        self._printer.commands(["G28 O", "G29 P3 T1"])

    def try_parse_meshProbingProgress(self, line):
        gcode_match = self._meshProbingProgressPattern.match(line)
        if gcode_match is None:
            return
        current = int(gcode_match.group(1))
        total = int(gcode_match.group(2))
        self._send_plugin_message(
            {
                "type": "meshProbingProgress",
                "current": current,
                "total": total,
            },
        )
