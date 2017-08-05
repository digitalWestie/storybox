#!/bin/bash

echo "Moving playlists..."

find /home/pi/storybox/ -name '*.m3u' -exec mv '{}' /home/pi/.kodi/userdata/playlists/music \;

echo "Done."

sleep 2