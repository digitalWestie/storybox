#!/bin/bash

echo "Moving playlists..."

find /home/pi/storybox/ -name '*.m3u' -exec mv '{}' /home/pi/Desktop \;

echo "Done."

sleep 2
