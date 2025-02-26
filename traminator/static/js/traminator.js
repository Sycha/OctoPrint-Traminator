console.log("Tram: Included");
$(function () {
    console.log("Tram: On Ready");

    var tab_id = "#tab_plugin_traminator";

    function TraminatorViewModel(parameters) {
        var self = this;
        self.tram = function () {
            console.log("Tram: run tram");
            OctoPrint.simpleApiCommand("traminator", "tram").done(function (response) {
                console.log(response);
            });
        };

        self.wizard = function () {
            console.log("Tram: run wizard");
            OctoPrint.simpleApiCommand("traminator", "wizard").done(function (response) {
                var resultElements = $(`[data-traminator-coord]`)
                resultElements.text("...")
                console.log(response);
            });
        };

        self.probe = function (data, event) {
            var probeLocation = event.target.dataset.traminatorCoord.split(',');

            OctoPrint.simpleApiCommand("traminator", "probe", { "x": parseFloat(probeLocation[0]), "y": parseFloat(probeLocation[1]) }).done(function (response) {
                console.log(response);
            });

        }

        self.onDataUpdaterPluginMessage = function (plugin, data) {
            if (plugin != "traminator") {
                return
            }
            console.log("Tram: Recieved Plugin Message");
            if (data.type == "adjustment") {
                $(`#traminator-${data.screw.toLowerCase()}`).text(`${data.turn} (${data.offset} mm)`);
            }

            if (data.type == "probe") {
                var coord = `${data.x},${data.y}`;
                var resultElement = $(`[data-traminator-coord="${coord}"]`)
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