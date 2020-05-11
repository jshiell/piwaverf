import pigpio
import time

import lwrf


class LightCommand:
  On = 1
  Off = 0


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


  def send(self, room_id, unit_number, command):    
    self._tx.put(self._build_message(room_id, unit_number, command), self._tx_repeat)
  

  def _build_message(self, room_id, unit_number, command):
    message = [0, 0, unit_number, command]

    for element in self._transmitter_id:
      message.append(int(element, base=16))

    message.append(room_id)

    if len(message) != 10:
      raise ValueError(f'Malformed message: {message}')

    return message
