import pigpio
import time
import yaml
import socket
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


class Hub:

    _DEFAULT_BIND_ADDRESS = '0.0.0.0'
    _DEFAULT_PORT = 9760


    def __init__(self, controller, bind_address=_DEFAULT_BIND_ADDRESS, port=_DEFAULT_PORT):
      self._controller = controller
      self._bind_address = bind_address
      self._port = port


    def start(self):
      self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self._sock.bind((self._bind_address, self._port))

      try:
        while True:
          data, _ = self._sock.recvfrom(1024)
          if not data:
            break

          self._handle_message(data)

      except OSError:
        self._sock.close()

    
    def _handle_message(self, data):
      message = data.decode('utf-8')

      if message[4] == 'F':
        print(f'Pairing command, ignoring {message}')
        next

      if message[5] == 'R' and message[7] == 'D' and message[9] == 'F':
        room_number = int(message[6])
        device_number = int(message[8])
        function = int(message[10])

        command = self._map_command(function)
        if command is not None:
          print(f'Sending command {command} to device {device_number} in room {room_number}')
          self._controller.send(room_number, device_number, command)
 

    def _map_command(self, function):
      if function == 0:
        return LightCommand.Off
      elif function == 1:
        return LightCommand.On
      else:
        print(f'Unknown function in message: {message}')
        return None


    def shutdown(self):
      self._sock.close()


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
