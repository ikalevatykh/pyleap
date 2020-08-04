"""This module contains the hand visualisation helper."""

from threading import Lock, Thread
from typing import Optional, Tuple

import numpy as np

from panda3d_viewer import Viewer, ViewerConfig, ViewerClosedError

from .leap import Controller, Frame, Hand, Listener
from .model import HandModel, HandModelBase

__all__ = ('LeapViewer', 'MultiHandView', 'HandView')


class HandView:
    """Hand visualisation helper class."""

    def __init__(self, viewer: Viewer, model: HandModelBase, hand: Hand, color: Tuple):
        """Append the hand model to the viewer."""
        self._viewer = viewer
        self._model = model
        self._group = f'leap_{hand.id}'
        self._viewer.append_group(self._group)

        for key, (length, width) in self._model.bones(hand).items():
            frame = (0.0, 0.0, length / 2.0), (1.0, 0.0, 0.0, 0.0)
            self._viewer.append_capsule(self._group, key, width / 2.0, length, frame)
            self._viewer.set_material(self._group, key, color)

    def update(self, hand: Hand) -> None:
        """Update bone positions."""
        self._viewer.move_nodes(self._group, self._model.frames(hand))

    def remove(self) -> None:
        """Remove the hand model from the viewer."""
        self._viewer.remove_group(self._group)


class MultiHandView:
    """Multiple hand visualisation helper class."""

    def __init__(self, viewer: Viewer, model: HandModelBase):
        """Init view."""
        self._viewer = viewer
        self._model = model
        self._hands = {}

    def update(self, frame: Frame) -> None:
        """Update hands states."""
        hands = {}
        for hand in frame.hands:
            if hand.id not in self._hands:
                color = (1, 0, 0, 1) if hand.is_left else (0, 1, 0, 1)
                view = HandView(self._viewer, self._model, hand, color)
            else:
                view = self._hands.pop(hand.id)
            view.update(hand)
            hands[hand.id] = view
        for view in self._hands.values():
            view.remove()
        self._hands = hands


class LeapViewer(Listener):
    """Leap hands viewer."""

    def __init__(self,
                 config: Optional[ViewerConfig] = None,
                 model: Optional[HandModelBase] = None):
        super().__init__()
        self._config = config
        self._model = model or HandModel()
        self._lock = Lock()
        self._frame = None

    def on_frame(self, controller: Controller) -> None:
        with self._lock:
            self._frame = controller.frame()

    def run(self) -> None:
        config = self._config or ViewerConfig(scene_scale=10.0)
        viewer = Viewer(window_title='LeapMotion', config=config)
        viewer.reset_camera(pos=(5, 5, 5), look_at=(0, 0, 1))
        hands_view = MultiHandView(viewer, self._model)

        while True:
            try:
                with self._lock:
                    frame = self._frame
                if frame is not None:
                    hands_view.update(frame)
                viewer._app.step()
            except ViewerClosedError:
                break
