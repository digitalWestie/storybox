#!/bin/bash

clear

cd ~/storybox

lxterminal -e python ~/storybox/generate_playlists.py

lxterminal -e ~/storybox/move_playlists.sh