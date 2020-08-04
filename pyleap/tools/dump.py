"""This application collect data from the Leap Motion device."""

import argparse

from ..leap import Controller, Listener
from ..serialize import FileWriter
from ..viewer import LeapViewer

parser = argparse.ArgumentParser('Collect data')
parser.add_argument('--file', type=str, help='Path to output file')


def main(args):
    viewer = LeapViewer()
    writer = FileWriter(args.file)

    controller = Controller()    
    controller.add_listener(writer)
    controller.add_listener(viewer)
    viewer.run()
    controller.remove_listener(viewer)
    controller.remove_listener(writer)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
