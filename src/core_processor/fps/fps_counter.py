import collections
from typing import Dict, List

from src.cameras.capture.frame_payload import FramePayload


class FPSCounter:
    def __init__(self):
        self._frame_timestamps = collections.deque(maxlen=500)

    @property
    def current_fps(self):
        current_length = len(self._frame_timestamps)

        if current_length <= 2:
            return 0.0

        return current_length / (
            (self._frame_timestamps[-1] - self._frame_timestamps[0]) / 1e9
        )

    def increment(self, frame: FramePayload):
        self._frame_timestamps.append(frame.timestamp)


class FPSCamCounter:
    def __init__(self, webcam_ids: List[str]):
        self._webcam_ids = webcam_ids
        self._counters: Dict[str, FPSCounter] = self._init_counters(webcam_ids)

    def _init_counters(self, webcam_ids: List[str]):
        d = {}
        for webcam_id in webcam_ids:
            d[webcam_id] = FPSCounter()

        return d

    def increment_frame_processed_for(self, webcam_id, frame: FramePayload):
        self._counters[webcam_id].increment(frame)

    def current_fps_for(self, webcam_id):
        return self._counters[webcam_id].current_fps
