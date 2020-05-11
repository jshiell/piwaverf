import lwrf


def build_message(transmitter_id, sub_id, unit_number, command):
  if len(transmitter_id) != 5:
    raise ValueError(f'Transmitter ID must be five hex characters, found: {transmitter_id}')

  message = [0, 0, unit_number, command]
  for element in transmitter_id:
    message.append(int(element, base=16))

  message.append(sub_id)

  if len(message) != 10:
    raise ValueError(f'Malformed message: {message}')

  return message


if __name__ == "__main__":
  import time
  import pigpio
  import lwrf

  TRANSMITTER_ID = 'f1234'
  SUB_ID = 1
  UNIT_NUMER = 1
  COMMAND = 1 # 0 = off, 1 = on

  TX_GPIO_PIN = 18
  TX_REPEAT = 12

  pi = pigpio.pi()
  tx = lwrf.tx(pi, TX_GPIO_PIN)

  tx.put(build_message(TRANSMITTER_ID, SUB_ID, UNIT_NUMBER, COMMAND), TX_REPEAT)

  tx.cancel()
  pi.stop()
  time.sleep(2)
