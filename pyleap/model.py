"""This module contains the hand visualisation helper."""

from typing import Any, Dict, Tuple
import abc

import numpy as np
from transforms3d.euler import mat2euler

from panda3d_viewer import Viewer

from .leap import Frame, Hand, Matrix, Vector

__all__ = ('HandModel', 'HandModelBase')


class HandModelBase(abc.ABC):

    @abc.abstractclassmethod
    def bones(self, hand: Hand) -> Dict[str, Tuple]:
        """Hand bones.

        Arguments:
            hand {Hand} -- sample from the LeapMotion device

        Returns:
            Dict -- dictionary of 'bone name' : '(bone length, bone width)' pairs
        """

    @abc.abstractclassmethod
    def frames(self, hand: Hand, z_up: bool = True) -> Dict[str, np.ndarray]:
        """Link frames.

        Arguments:
            hand {Hand} -- sample from the LeapMotion device
            z_up {bool} -- use 

        Returns:
            Dict -- dictionary of 'bone name' : 'transformation matrix in the global CS' pairs
        """

    @abc.abstractclassmethod
    def angles(self, hand: Hand) -> Dict[str, np.ndarray]:
        """Joint angles.

        Arguments:
            hand {Hand} -- sample from the LeapMotion device

        Returns:
            Dict -- dictionary of 'bone name' : 'parent joint's euler angles' pairs
        """


class HandModel(HandModelBase):
    """Hand model."""

    FINGERS = ['thumb', 'index', 'middle', 'ring', 'pinky']

    def bones(self, hand: Hand) -> Dict[str, Tuple]:
        """Hand bones.

        Arguments:
            hand {Hand} -- sample from the LeapMotion device

        Returns:
            Dict -- dictionary of 'bone name' : '(bone length, bone width)' pairs
        """
        bones = {'wrist': (0.0, mm2m(hand.arm.width))}

        for finger, finger_id in zip(hand.fingers, self.FINGERS):
            for b in range(4):
                key = f'{finger_id}{b}'
                bones[key] = (mm2m(finger.bone(b).length), mm2m(finger.bone(b).width))

        return bones

    def frames(self, hand: Hand, z_up: bool = True) -> Dict[str, np.ndarray]:
        """Link frames.

        Arguments:
            hand {Hand} -- sample from the LeapMotion device

        Returns:
            Dict -- dictionary of 'bone name' : 'frame matrix in the global CS' pairs
        """
        frames = {
            'elbow': basis2mat(hand.arm.basis, hand.arm.elbow_position),
            'wrist': basis2mat(hand.basis, hand.wrist_position),
            'palm': basis2mat(hand.basis, hand.palm_position)}

        for finger, finger_id in zip(hand.fingers, self.FINGERS):
            for b in range(5):
                key = f'{finger_id}{b}'
                frames[key] = basis2mat(finger.bone(b).basis, finger.joint_position(b))

        if hand.is_left:
            l2r = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
            for key in frames:
                frames[key] = frames[key] @ l2r

        if z_up:
            y2z = [[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]
            for key in frames:
                frames[key] = y2z @ frames[key]

        return frames

    def angles(self, hand: Hand) -> Dict[str, np.ndarray]:
        """Joint angles.

        Arguments:
            hand {Hand} -- sample from the LeapMotion device

        Returns:
            Dict -- dictionary of 'bone name' : 'parent joint euler angles' pairs
        """
        frames = self.frames(hand)
        angles = {'wrist': mat2euler(np.linalg.inv(frames['elbow']) @ frames['wrist'])}

        for finger_id in self.FINGERS:
            for b in range(4):
                key = f'{finger_id}{b}'
                if b > 0:
                    angles[key] = mat2euler(np.linalg.inv(frame) @ frames[key])
                frame = frames[key]

        return angles


def mm2m(value: Any) -> Any:
    """Convert value from millimeters to meters.

    Arguments:
        value {Any} -- value in millimeters

    Returns:
        Any -- value in meters
    """
    return value * 0.001


def basis2mat(basis: Matrix, origin: Vector) -> np.ndarray:
    """Convert basis from LM format to homogenous matrix 4x4.

    Arguments:
        basis {Matrix} -- frame orientation
        origin {Vector} -- frame origin

    Returns:
        np.ndarray -- homogenous matrix
    """
    basis.origin = mm2m(origin)
    array = basis.to_array_4x4()
    return np.asarray(array).reshape((4, 4)).T
