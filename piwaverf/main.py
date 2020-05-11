#!/usr/bin/env python3

import piwaverf
import time
import sys
import argparse


DEFAULT_TRANSMITTER_ID = 'f1234'
DEFAULT_ROOM_ID = 1
DEFAULT_UNIT_NUMER = 1


def print_usage(argv):
  print(f'{argv[0]} <--help> | --command <pair|on|off> ' +
        '--room <room:0-14={DEFAULT_ROOM_ID}> ' +
        '--unit <unit:0-15={DEFAULT_UNIT_NUMER}> ' +
        '[--transmitter=<transmitter-id={DEFAULT_TRANSMITTER_ID}>]\n')
  print('Commands:')
  print('  pair - send a pairing request to a device. Ensure the device is in pairing mode first.')
  print('  on - turn a light on.')
  print('  off - turn a light off.')


def main(argv):
  parser = argparse.ArgumentParser(description='Control LightwaveRF lights')
  parser.add_argument('command', choices=['pair', 'on', 'off'],
                      help='The action to take on the device')
  parser.add_argument('-t', '--transmitter', dest='transmitter',
                      default=DEFAULT_TRANSMITTER_ID, help='The ID of the transmitter')
  parser.add_argument('-r', '--room', dest='room', type=int,
                      default=DEFAULT_ROOM_ID, help='The ID of the room')
  parser.add_argument('-u', '--unit', dest='unit', type=int,
                      default=DEFAULT_UNIT_NUMER, help='The unit number')

  args = parser.parse_args()

  controller = piwaverf.Controller(args.transmitter)

  if args.command == 'pair':
    controller.send(args.room, args.unit, piwaverf.LightCommand.Off)
  elif args.command == 'on':
    controller.send(args.room, args.unit, piwaverf.LightCommand.On)
  elif args.command == 'off':
    controller.send(args.room, args.unit, piwaverf.LightCommand.Off)

  controller.shutdown()


if __name__ == "__main__":
  main(sys.argv)
