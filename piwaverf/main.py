if __name__ == "__main__":
  import piwaverf
  import time

  TRANSMITTER_ID = 'f1234'

  controller = piwaverf.Controller(TRANSMITTER_ID)

  ROOM_ID = 1
  UNIT_NUMER = 1

  controller.send(ROOM_ID, UNIT_NUMER, piwaverf.LightCommand.On)

  time.sleep(10)

  controller.send(ROOM_ID, UNIT_NUMER, piwaverf.LightCommand.Off)

  controller.shutdown()
