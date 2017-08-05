## Running python keyboard

If you get errors it maybe interface isn't detected, try:

`sudo modprobe i2c_bcm2708`

To run in the background: 

`sudo python keyboard.py &`

Then to stop it, find process: 

`ps aux | grep keyboard.py`

And then kill it: 

`sudo kill <pid of keyboard.py>`


## Controlling Kodi 

The control script uses this library (https://github.com/jcsaaddupuy/python-xbmc) to send json-rpc requests. You can find examples on that page. 

A list of all the API commands can be found by enabling webserver and navigating to:

`http://localhost:8080/jsonrpc`


## Controlling USB power with hub-ctrl

Reset all USB and ETH ports

```
sudo ./hub-ctrl -h 0 -P 2 -p 0 
sleep 3
sudo ./hub-ctrl  -h 0 -P 2 -p 1
```

Reset USB 4 (bottom left port)

```
sudo ./hub-ctrl -h 0 -P 3 -p 0
sleep 3
sudo ./hub-ctrl  -h 0 -P 3 -p 1
```
 
## hub-ctrl port numbering

-P 1 -- Controls the Ethernet port
-P 2 -- Controls all four USB ports (not the Ethernet)
-P 3 -- Controls USB Port 4 (bottom left port)
-P 4 -- Controls USB Port 2 (top right port)
-P 5 -- Controls USB Port 3 (bottom right port)
