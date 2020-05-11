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
* Ground to pin 3 (Ground)

It's also worth adding on an antenna to the board - 170mm of wire should be about a quarter-wavelength.

![Transmitter with pins highlighted](docs/transmitter.jpg)

## Prerequisies

* [Rasbpian](https://www.raspberrypi.org/downloads/) 10.3 (in this case, shouldn't be particularly tied to it)
* [Pigpio](http://abyz.me.uk/rpi/pigpio/):

   ```bash
   sudo apt install pigpio
   sudo systemctl enable pigpiod
   sudo systemctl start pigpiod
   ```

## Usage

Only basic functions are supported at present (lights on/off).

Firstly, you'll need to set up your device mappings. This maps from the names used by the UDP protocol to the IDs used by the radio protocol. To do this we use a YAML file in a subset of the format used by Paul Clarke's popular [LightwaveRF Gem](https://github.com/pauly/lightwaverf).

```yaml
room:
- name: A Room
  device:
  - name: Telly Lights
    id: D7
  - name: Door Lights
    id: D2
- name: Another Room
  device:
  - name: Lights
```

The IDs of the rooms and devices will be determined by the `id` attribute (only the numeric part will be used), or the index within the list if no `id` is present. e.g. `A Room`/`Telly Lights` would be `room_id=1` and `device_id=7`. `Another Room`/`Lights` would be `room_id=2` and `device_id=1`.

You can have up to 8 rooms, and up to 15 devices per room. The protocol allows for more rooms, but I believe this matches the limits imposed by the app.

```bash
pip install -r requirements.txt

pywaverf/main.py --help # show usage info
```

You'll need to ensure your devices are paired, or they'll ignore the messages from the hub. Make sure the device is in pairing mode before doing so, or the message will have no effect.

```bash
pywaverf/main.py pair --room 'A Room' --device 'Door Lights'
```

Once paired, you can test by sending messages directly:

```bash
pywaverf/main.py on --room 'Another Room' --device 'Lights' # turn a paired unit on
pywaverf/main.py off --room 'Another Room' --device 'Lights' # and off again
```

You can finally start the listener for UDP messages:

```bash
pywaverf/main.py listen
```

You can then send test messages with the [LightwaveRF Gem](https://github.com/pauly/lightwaverf), or via `netcat`:

```bash
echo '666,!R1D5F1|ignored|ignored' | nc -w 1 -u <address-of-listening-host> 9760 # turn room 1 device 5 on
echo '666,!R1D5F0|ignored|ignored' | nc -w 1 -u <address-of-listening-host> 9760 # turn room 1 device 5 off
```

## References

* [433Mhz protocol](https://github.com/roberttidey/LightwaveRF/blob/master/LightwaveRF433.pdf)
* [UDP hub protocol](https://github.com/openremote/Documentation/wiki/LightwaveRF)
