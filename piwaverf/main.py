#!/usr/bin/env python3

import piwaverf
import time
import sys
import argparse
import signal
from pathlib import Path


DEFAULT_TRANSMITTER_ID = 'f1234'
DEFAULT_MAPPING_FILE = f'{Path.home()}/lightwaverf-config.yml'


def main(argv):
  parser = argparse.ArgumentParser(description='Control LightwaveRF lights')
  parser.add_argument('command', choices=['pair', 'on', 'off', 'listen'],
                      help='The action to perform')
  parser.add_argument('-r', '--room', dest='room_name',
                      help='The name of the room for pair/on/off')
  parser.add_argument('-d', '--device', dest='device_name',
                      help='The name of the device for pair/on/off')
  parser.add_argument('-t', '--transmitter', dest='transmitter',
                      default=DEFAULT_TRANSMITTER_ID, help='The ID of the transmitter')
  parser.add_argument('-m', '--mapping', dest='mapping_file',
                      default=DEFAULT_MAPPING_FILE, help='The mapping file for room/device names to indices')

  args = parser.parse_args()

  if args.command in ['pair', 'on', 'off'] and (args.room_name is None or args.device_name is None):
    print('Room & device are required for command pair, on, and off')
    sys.exit(2)

  controller = piwaverf.Controller(args.transmitter)
  if args.command in ['pair', 'on', 'off']:
    mappings = piwaverf.DeviceMappings(args.mapping_file)

    device = mappings.device_id(args.room_name, args.device_name)
    if device is None:
      print(f'Could not locate device "{args.device_name}" in room "{args.room_name}" in mappings file "{args.mapping_file}", exiting.')
      sys.exit(1)

    print(f'Sending "{args.command}" to device "{args.device_name}" ({device.device_id}) in room "{args.room_name}" ({device.room_id})')

    if args.command == 'pair':
      controller.send(device.room_id, device.device_id, piwaverf.LightCommand.Off)
    elif args.command == 'on':
      controller.send(device.room_id, device.device_id, piwaverf.LightCommand.On)
    elif args.command == 'off':
      controller.send(device.room_id, device.device_id, piwaverf.LightCommand.Off)

  elif args.command == 'listen':
    print('Starting in listen mode')

    hub = piwaverf.Hub(controller)

    def hub_shutdown(sig, frame):
      print('Shutting down...')
      hub.shutdown()
    signal.signal(signal.SIGINT, hub_shutdown)

    hub.start()

  controller.shutdown()


if __name__ == "__main__":
  main(sys.argv)
