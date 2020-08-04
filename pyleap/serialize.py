import ctypes
import pickle
import time
from threading import Lock, Thread
from typing import ByteString

from .leap import Controller, Frame, Listener, byte_array

__all__ = ('Serializer', 'FileWriter', 'FileReader')


class Serializer:
    """Serialize helper class."""

    @staticmethod
    def dump(frame: Frame) -> ByteString:
        """Serialize leap frame.

        Arguments:
            frame {Frame} -- frame to serialize

        Returns:
            ByteString -- byte representation of the frame
        """
        data, length = frame.serialize
        ptr = data.cast().__int__()
        buffer = (ctypes.c_ubyte * length).from_address(ptr)
        return bytes(buffer)

    @staticmethod
    def load(buffer: ByteString) -> Frame:
        """Deserialize leap frame.

        Arguments:
            buffer {ByteString} -- byte representation of the frame

        Returns:
            Frame -- deserialized frame
        """
        frame = Frame()
        data, length = byte_array(len(buffer)), len(buffer)
        for i in range(length):
            data[i] = buffer[i]
        frame.deserialize((data, length))
        return frame


class FileWriter(Listener):
    """Helper class to serilize frames to a file."""

    def __init__(self, filename: str):
        super().__init__()
        self._filename = filename
        self._buffer = []

    def on_frame(self, controller) -> None:
        frame = controller.frame()
        self._buffer.append(Serializer.dump(frame))

    def on_exit(self, controller) -> None:
        print('Processing...')
        with open(self._filename, 'wb') as f:
            pickle.dump(self._buffer, f)
        print(f'Saved {len(self._buffer)} records to "{self._filename}".')


class FileReader(Thread):
    """Helper class to deserilize frames from a file."""

    def __init__(self, filename: str):
        super().__init__()
        self._filename = filename
        self._running = True
        self._listeners = []
        self._frame = None
        self._lock = Lock()

    def add_listener(self, listener) -> None:
        with self._lock:
            self._listeners.append(listener)

    def frame(self) -> Frame:
        return self._frame

    def run(self) -> None:
        with open(self._filename, 'rb') as f:
            buffer = pickle.load(f)
        print(f'Loaded {len(buffer)} records from "{self._filename}".')

        timestamp = 0
        for record in buffer:
            if not self._running:
                break
            self._frame = Serializer.load(record)
            if timestamp:
                time.sleep((self._frame.timestamp - timestamp) / 1e6)
            timestamp = self._frame.timestamp
            with self._lock:
                for l in self._listeners:
                    l.on_frame(self)

    def stop(self):
        self._running = False
        self.join()
