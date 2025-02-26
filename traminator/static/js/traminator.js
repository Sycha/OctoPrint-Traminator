console.log("Tram: Included");
$(function () {
    console.log("Tram: On Ready");

    var tab_id = "#tab_plugin_traminator";

    function TraminatorViewModel(parameters) {
        var self = this;

        self.wizard = function () {
            console.log("Tram: run wizard");
            OctoPrint.simpleApiCommand("traminator", "wizard").done(function (response) {
                var resultElements = $(`[data-traminator-location]`)
                resultElements.text("...")
                console.log(response);
            });
        };

        self.probe = function (data, event) {
            var location = event.target.dataset.traminatorLocation;

            OctoPrint.simpleApiCommand("traminator", "probe", { "location": parseInt(location) }).done(function (response) {
                console.log(response);
            });

        }

        self.onDataUpdaterPluginMessage = function (plugin, data) {
            if (plugin != "traminator") {
                return
            }

            console.log("Tram: Recieved Plugin Message");
            if (data.type == "probe") {
                var location = `${data.location}`;
                var resultElement = $(`[data-traminator-location="${location}"]`)
                resultElement.text(`${data.advice} (${data.z} mm)`)
            }
        }
    }
    OCTOPRINT_VIEWMODELS.push({
        construct: TraminatorViewModel,
        dependencies: [
            "printerStateViewModel",
        ],
        elements: [tab_id],
    });;
    console.log("Tram: On Ready Complete");
})