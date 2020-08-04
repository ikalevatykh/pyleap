"""This application visualise the Leap Motion device detections."""

import argparse

from ..leap import Controller, Listener
from ..serialize import FileReader
from ..viewer import LeapViewer

parser = argparse.ArgumentParser('Show hand skeleton')
parser.add_argument('-f', '--file', type=str, default=None, help='Path to recorded data')


def main(args):
    controller = Controller()
    viewer = LeapViewer()

    if args.file is not None:
        reader = FileReader(args.file)
        reader.add_listener(viewer)
        reader.start()
        viewer.run()
        reader.stop()
    else:        
        controller.add_listener(viewer)
        viewer.run()
        controller.remove_listener(viewer)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
