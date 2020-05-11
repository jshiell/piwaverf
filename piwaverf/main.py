#!/usr/bin/env python3

import piwaverf
import time
import sys
import argparse
from pathlib import Path


DEFAULT_TRANSMITTER_ID = 'f1234'
DEFAULT_MAPPING_FILE = f'{Path.home()}/lightwaverf-config.yml'


def main(argv):
  parser = argparse.ArgumentParser(description='Control LightwaveRF lights')
  parser.add_argument('command', choices=['pair', 'on', 'off'],
                      help='The action to take on the device')
  parser.add_argument('-r', '--room', dest='room_name', required=True,
                      help='The name of the room')
  parser.add_argument('-d', '--device', dest='device_name', required=True,
                      help='The name of the device')
  parser.add_argument('-t', '--transmitter', dest='transmitter',
                      default=DEFAULT_TRANSMITTER_ID, help='The ID of the transmitter')
  parser.add_argument('-m', '--mapping', dest='mapping_file',
                      default=DEFAULT_MAPPING_FILE, help='The mapping file for room/device names to indices')

  args = parser.parse_args()

  mappings = piwaverf.DeviceMappings(args.mapping_file)

  device = mappings.device_id(args.room_name, args.device_name)
  if device is None:
    print(f'Could not locate device "{args.device_name}" in room "{args.room_name}" in mappings file "{args.mapping_file}", exiting.')
    sys.exit(1)

  print(f'Sending "{args.command}" to device "{args.device_name}" ({device.device_id}) in room "{args.room_name}" ({device.room_id})')

  controller = piwaverf.Controller(args.transmitter)
  if args.command == 'pair':
    controller.send(device.room_id, device.device_id, piwaverf.LightCommand.Off)
  elif args.command == 'on':
    controller.send(device.room_id, device.device_id, piwaverf.LightCommand.On)
  elif args.command == 'off':
    controller.send(device.room_id, device.device_id, piwaverf.LightCommand.Off)

  controller.shutdown()


if __name__ == "__main__":
  main(sys.argv)
