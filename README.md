# water-monitor
A micropython experiment to track water usage

Using a Raspberry Pi Pico W board with a MAX4466 
microphone, can you monitor your water usage 
acoustically?

Using a 3D-printed pipe mount for the microphone,
get real-time push notifications using IFTTT on
your phone whenever water turns on or off.


### Hardware Connections

Using a MAX4466 analog mic with a Raspberry Pi Pico W:

Connect OUT on the mic to ADC2 (GPIO28, Pin 34) 


### Requirements

To run the build script on your machine, you need to pip install:

* pyserial
* adafruit-ampy

### Building

__Important: Make sure your board is already plugged in 
to a USB port on your and has micropython installed.__

```commandline
git clone https://github.com/jsmillie7/water-monitor.git ~/water-monitor
cd ~/water-monitor
./build.py
```

The first time you run the build script, it will ask
a series of questions and write them locally to a json
data file.

That data file will be written to the board, as will several
python files.
