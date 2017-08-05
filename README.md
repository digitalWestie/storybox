# STORYBOX

## Setting up Kodi

Install kodi 17.1 Git:20170401-7804a92-dirty Media Center Kodi 


To install the skin for kodi. Copy the `skin.storybox` folder (the skin) into `.kodi/addons`. Also important are the skin settings in the `addon_data` folder which should go into `.kodi/userdata`.  

The skin settings help achieve the minimal kiosk-style interface with several of the menu buttons disabled. It also disables the 'settings' item, but this can still be activated by pressing the 'S' key in the kodi home.

Once the addons are installed you will need to setup the webserver so that we can control Kodi with the capacitive touch script. Follow the guide here: 

http://kodi.wiki/view/Webserver#Enabling_the_webserver

In the touch script I've set it up to connect with the username and password to "kodi". 


## Creating the playlists

Put all audio files, and the CSV file detailing metadata/categories into a folder called 'recordings'. 

Run the `generate_playlists.py` script to set ID tags and create playlists. i.e. `python generate_playlists.py`.

Move all the playlist files into the Kodi playlist directory, this should be `/home/pi/.kodi/userdata/playlists/music`.

You can now go into Kodi and associate menu items with the playlists.


## Setting up capacitive touch

Install capacitive touch system: https://learn.adafruit.com/mpr121-capacitive-touch-sensor-on-raspberry-pi-and-beaglebone-black/usage


## Startup scripts

Set the storybox UI to show on startup by adding new lines to `nano ~/.config/lxsession/LXDE-pi/autostart`. 
This new line should start with "@" + scriptname (including path to script if necessary): 

So the `autostart` file should look something like this:

```
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xscreensaver -no-splash
@/home/pi/storybox/startkodi.sh
@/home/pi/storybox/startkeyb.sh
```
