# PiWaveRF

Turning a Raspberry Pi into a first-gen LightwaveRF hub.

Currently at a very early stage, but the goal is to allow light control via the same UDP protocol as the Hub, hence allowing it to work with the [Homebridge plugin](https://github.com/rooi/homebridge-lightwaverf).

This is very much in debt to [Robert Tidey's LightwaveRF work](https://github.com/roberttidey/LightwaveRF), and uses his transmission logic.

## Hardware

* A [433Mhz transmitter module](https://www.amazon.co.uk/gp/product/B07B9KV8D9/)
* 3 x [Female-to-female jumper cables](https://www.amazon.co.uk/gp/product/B01EV70C78/)
* A [Raspberry Pi](https://www.raspberrypi.org/products/), in my case a 3B+.

## Wiring

Given the [GPIO port](https://www.raspberrypi.org/documentation/usage/gpio/):

* Data to pin 12 (GPIO18)
* 5V to pin 1 (5V)
* Ground to ping 3 (Ground)

It's also worth adding on an antenna to the board - 170mm of wire should be about a quarter-wavelength.

## Prerequisies

* [Rasbpian](https://www.raspberrypi.org/downloads/) 10.3 (in this case, shouldn't be particularly tied to it)
* [Pigpio](http://abyz.me.uk/rpi/pigpio/):

   ```bash
   sudo apt install pigpio
   sudo systemctl enable pigpiod
   sudo systemctl start pigpiod
   ```

## Usage

This is at a very early stage at present. However, you can use `piwaverf.py` to pair and turn a light on/off. With the current code, place the switch into pairing mode (hold both buttons until it begines to flash) and then run `piwaverf.py`. It will pair the light to the hard-coded transmitter and unit ID. Running it a second time will turn the light on. Change `COMMAND` to `0` and run again to turn it off.

## References

* [433Mhz protocol](https://github.com/roberttidey/LightwaveRF/blob/master/LightwaveRF433.pdf)
* [UDP hub protocol](https://github.com/openremote/Documentation/wiki/LightwaveRF)
