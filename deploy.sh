#!/bin/bash

rsync -vah --delete ./traminator $OCTOPRINTHOST:/home/pi/.octoprint/plugins


curl -X POST --header "X-Api-Key: $APIKEY" http://$OCTOPRINTHOST/api/system/commands/core/restart