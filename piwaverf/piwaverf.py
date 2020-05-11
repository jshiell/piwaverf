import pigpio
import time
import yaml
from dataclasses import dataclass

import lwrf


class LightCommand:
  On = 1
  Off = 0


@dataclass
class Device:
  room_id: int
  device_id: int


class DeviceMappings:
  """Read device mappings from a LightwaveRF Gem (https://github.com/pauly/lightwaverf) 
     compatible file."""


  def __init__(self, filename):
    with open(filename, 'r') as fh:
      self._config = yaml.safe_load(fh)

  
  def device_id(self, room_name, device_name):
    room_index = 1
    for room in self._config['room']:
      if room.get('name').lower() == room_name.lower():
        room_id = room.get('id') or room_index
        device_index = 1

        for device in room['device']:
          if device.get('name').lower() == device_name.lower():
            return Device(room_id, self._device_int(device.get('id')) or device_index)

          device_index += 1

      room_index += 1
    
    return None


  def _device_int(self, string_value):
    if string_value is not None:
      return [int(s) for s in string_value if s.isdigit()][0]
    else:
      return None


class Controller:

  _DEFAULT_TX_GPIO_PIN = 18
  _DEFAULT_TX_REPEAT = 12


  def __init__(self, transmitter_id, tx_gpio_pin=_DEFAULT_TX_GPIO_PIN, tx_repeat=_DEFAULT_TX_REPEAT):
    if len(transmitter_id) != 5:
      raise ValueError(f'Transmitter ID must be five hex characters, found: {transmitter_id}')
    self._transmitter_id = transmitter_id
    self._tx_repeat = tx_repeat

    self._pi = pigpio.pi()
    self._tx = lwrf.tx(self._pi, tx_gpio_pin)


  def shutdown(self):
    self._tx.cancel()
    self._pi.stop()
    time.sleep(2)


  def send(self, udp_room_id, udp_device_number, command):
    if udp_room_id < 1 or udp_room_id > 8:
      raise ValueError(f'UDP Room ID must be between 1 and 8 inclusive, currently {udp_room_id}')
    if udp_device_number < 1 or udp_device_number > 15:
      raise ValueError(f'UDP Device ID must be between 1 and 15 inclusive, currently {udp_device_number}')

    self._tx.put(self._build_message(udp_room_id - 1, udp_device_number - 1, command), self._tx_repeat)
  

  def _build_message(self, room_id, unit_number, command):
    message = [0, 0, unit_number, command]

    for element in self._transmitter_id:
      message.append(int(element, base=16))

    message.append(room_id)

    if len(message) != 10:
      raise ValueError(f'Malformed message: {message}')

    return message
