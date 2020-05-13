import pigpio
import time
import yaml
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import lwrf


class LightCommand:
  Off = 0
  On = 1
  Dim = 2


@dataclass
class Device:
  room_id: int
  device_id: int


class ResponseStatus:
  OK = 'OK'
  ERROR = 'ERR'


@dataclass
class Response:
  transaction_id: int
  status: str
  room_number: int = 1
  device_number: int = 1
  command: int = 0
  argument: int = 0
  error_code: int = 0
  error_message: str = ''


@dataclass
class ParsedCommand:
  identitifer: int
  argument: int = 0


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
    _DEFAULT_RX_PORT = 9760
    _DEFAULT_TX_PORT = 9671
    _DUMMY_MAC_ADDRESS = 'a1:b2:c3:d4:e6:f6'


    def __init__(self, controller, bind_address=_DEFAULT_BIND_ADDRESS, rx_port=_DEFAULT_RX_PORT, tx_port=_DEFAULT_TX_PORT, mac_address=_DUMMY_MAC_ADDRESS):
      self._controller = controller
      self._bind_address = bind_address
      self._rx_port = rx_port
      self._tx_port = tx_port
      self._mac_address = mac_address

      self._response_id = 1


    def start(self):
      self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self._socket.bind((self._bind_address, self._rx_port))

      try:
        with ThreadPoolExecutor(max_workers=1) as executor:
          while True:
            data, from_host = self._socket.recvfrom(1024)
            if not data:
              break

            response = self._handle_message(data, executor)
            self._socket.sendto(self._format_simple_response_message(response), (from_host[0], self._tx_port))
            if response.status == ResponseStatus.OK:
              self._socket.sendto(self._format_json_response_message(response), (from_host[0], self._tx_port))
              self._response_id += 1

      except OSError:
        self._socket.close()


    def _format_simple_response_message(self, response):
      message = f'{response.transaction_id},{response.status}' 
      if response.status == ResponseStatus.ERROR:
        message += ',{response.error_code},"{response.error_message}"'
      return message.encode('utf-8')


    def _format_json_response_message(self, response):
      json_command = 'unknown'
      if response.command == LightCommand.On:
        json_command = 'on'
      elif response.command == LightCommand.Off:
        json_command = 'off'
      elif response.command == LightCommand.Dim:
        json_command = 'dim'

      message = f'*!{{"trans":{self._response_id},"mac":"{self._mac_address[9:]}","time":{int(time.time())},"pkt":"433T","fn":"{json_command}","room":{response.room_number} ,"dev":{response.device_number},"param":{response.argument}}}'
      return message.encode('utf-8')

    
    def _handle_message(self, data, executor):
      message = data.decode('utf-8')

      transaction_id = ''
      message_offset = 0

      if message[message_offset] == ':': # MAC prefix, ignore at present
        while message[message_offset] != ',':
          message_offset += 1
        message_offset += 1

      while message[message_offset] != ',':
        transaction_id += message[message_offset]
        message_offset += 1
      if len(transaction_id) == 0:
        transaction_id = '0'

      if message[message_offset] != ',' and message[message_offset + 1] != '!':
        print(f'Malformed message: {message}')
        return Response(transaction_id, ResponseStatus.ERROR, 1, 'Malformed message')
      message_offset += 2

      if message[message_offset] == 'R' and message[message_offset + 2] == 'D' and message[message_offset + 4] == 'F':
        room_number = int(message[message_offset + 1])
        device_number = int(message[message_offset + 3])

        function = ''
        message_offset += 5
        while message_offset < len(message) and message[message_offset] != '|':
          function += message[message_offset]
          message_offset += 1

        command = self._parse_command(function)
        if command is not None:
          executor.submit(self._send, room_number, device_number, command.identitifer, command.argument)
          return Response(transaction_id, ResponseStatus.OK, room_number, device_number, command.identitifer, command.argument)

      elif message[message_offset] == 'F':
        print(f'Pairing command, ignoring {message}')
        return Response(transaction_id, ResponseStatus.OK)

      return Response(transaction_id, ResponseStatus.ERROR, 2, 'Unrecognised command')


    def _send(self, room_number, device_number, command, argument):
      print(f'Sending command {command} with argument {argument} to device {device_number} in room {room_number}')
      self._controller.send(room_number, device_number, command, argument)
 

    def _parse_command(self, function):
      if function == '0':
        return ParsedCommand(LightCommand.Off)
      elif function == '1':
        return ParsedCommand(LightCommand.On)
      elif function.startswith('dP'):
        dim_level = int(function[2:])
        return ParsedCommand(LightCommand.Dim, dim_level)
      else:
        print(f'Unknown function in message: {function}')
        return None


    def shutdown(self):
      self._socket.close()


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


  def send(self, udp_room_id, udp_device_number, command, command_argument=None):
    if udp_room_id < 1 or udp_room_id > 8:
      raise ValueError(f'UDP Room ID must be between 1 and 8 inclusive, currently {udp_room_id}')
    if udp_device_number < 1 or udp_device_number > 15:
      raise ValueError(f'UDP Device ID must be between 1 and 15 inclusive, currently {udp_device_number}')

    radio_command = command
    radio_command_argument = 0

    if command == LightCommand.Dim:
      if command_argument == 0:
        radio_command = 0
      else:
        radio_command = 1
        radio_command_argument = 127 + command_argument

    message = self._build_message(udp_room_id - 1, udp_device_number - 1, radio_command, radio_command_argument)
    self._tx.put(message, self._tx_repeat)
  

  def _build_message(self, room_id, unit_number, command, argument=0):
    arg1 = (argument & 0xF0) >> 4
    arg2 = argument & 0xF

    message = [arg1, arg2, unit_number, command]

    for element in self._transmitter_id:
      message.append(int(element, base=16))

    message.append(room_id)

    if len(message) != 10:
      raise ValueError(f'Malformed message: {message}')

    return message
