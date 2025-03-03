console.log("Tram: Included");
$(function () {
  console.log("Tram: On Ready");

  var tab_id = "#tab_plugin_traminator";

  function TraminatorViewModel(parameters) {
    var self = this;

    self.targetTemperature = ko.observable(60);
    self.tramOffsets = [
      ko.observable(),
      ko.observable(),
      ko.observable(),
      ko.observable(),
    ];

    self.ublPointCount = ko.observable();
    self.ublAutoPointCurrent = ko.observable();
    self.ublAutoProbeProgressPercent = ko.observable();

    self.onBeforeBinding = function () {
      self.tramOffsetReset();
      self.ublPointCount(0);
      self.ublAutoPointCurrent(0);
      self.ublAutoProbeProgressPercent(0);
    };

    self.tramOffsetReset = function () {
      self.tramOffsets.forEach((t) => t("..."));
    };

    self.wizard = function () {
      console.log("Tram: run wizard");
      OctoPrint.simpleApiCommand("traminator", "wizard").done(function (
        response
      ) {
        self.tramOffsetReset();
        console.log(response);
      });
    };

    self.probe = function (location) {
      OctoPrint.simpleApiCommand("traminator", "probe", {
        location: location,
      }).done(function (response) {
        console.log(response);
      });
    };

    self.ublAutoProbe = function () {
      OctoPrint.simpleApiCommand("traminator", "ublAutoProbe").done(function (
        response
      ) {
        console.log(response);
      });
    };

    self.ublFillUnpopulated = function () {
      OctoPrint.simpleApiCommand("traminator", "ublFillUnpopulated").done(
        function (response) {
          console.log(response);
        }
      );
    };

    self.onDataUpdaterPluginMessage = function (plugin, data) {
      if (plugin != "traminator") {
        return;
      }

      console.log("Tram: Recieved Plugin Message");
      if (data.type == "probe") {
        self.tramOffsets[data.location](`${data.advice} (${data.z} mm)`);
      }

      if (data.type == "meshProbingProgress") {
        current = data.current;
        total = data.total;

        self.ublPointCount(total);
        self.ublAutoPointCurrent(current);
        self.ublAutoProbeProgressPercent(
          (parseFloat(current) / parseFloat(total)) * 100
        );
      }
    };
  }
  OCTOPRINT_VIEWMODELS.push({
    construct: TraminatorViewModel,
    dependencies: ["printerStateViewModel"],
    elements: [tab_id],
  });
  console.log("Tram: On Ready Complete");
});
