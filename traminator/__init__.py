from octoprint.plugin import TemplatePlugin, StartupPlugin, SimpleApiPlugin, AssetPlugin


CMD_TRAM = "tram"


class TraminatorPlugin(TemplatePlugin, StartupPlugin, SimpleApiPlugin, AssetPlugin):
    def on_after_startup(self):
        self._logger.info(
            f"Traminator: {self._identifier}, {self._basefolder}, {self.get_template_configs()}"
        )

    def get_template_configs(self):
        return [dict(type="tab", template="traminator_tab.jinja2")]

    def get_api_commands(self):
        return {
            CMD_TRAM: [],
        }

    def on_api_command(self, command, data):
        if command == CMD_TRAM:
            self._printer.is_ready()
            self._printer.commands("M80", "G28 O", "G35")

    def get_assets(self):
        return {"js": ["js/traminator.js"]}


__plugin_name__ = "Traminator"
__plugin_version__ = "1.0.0"
__plugin_description__ = "UI focused on making traming easy"
__plugin_pythoncompat__ = ">=3.7,<4"
__plugin_implementation__ = TraminatorPlugin()
