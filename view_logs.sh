#!/bin/bash

ssh $OCTOPRINTHOST bash -c "tail -f /home/pi/.octoprint/logs/octoprint.log"
#ssh $OCTOPRINTHOST bash -c "tail -f /home/pi/.octoprint/logs/octoprint.log | grep '[Tt]raminator'"