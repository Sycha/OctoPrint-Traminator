console.log("Tram: Included");
$(function () {
    console.log("Tram: On Ready");
    function TraminatorViewModel(parameters) {
        var self = this;
        console.log("Tram: ViewModel");
        self.tram = function () {
            console.log("Tram: Function");
            OctoPrint.simpleApiCommand("traminator", "tram").done(function (response) {
                console.log(response);
            });
        };
    }
    OCTOPRINT_VIEWMODELS.push({
        construct: TraminatorViewModel,
        dependencies: [
            "printerStateViewModel",
        ],
        elements: ["#tab_plugin_traminator"],
    });;
    console.log("Tram: On Ready Complete");
})