import logging
import time

import cv2

from src.cameras.capture.frame_payload import FramePayload

logger = logging.getLogger(__name__)


class FrameGrabber:
    @staticmethod
    def get(video_capture: cv2.VideoCapture):
        timestamp_ns_pre_grab = time.time_ns()
        # Why grab not read? see ->
        # https://stackoverflow.com/questions/57716962/difference-between-video-capture-read-and
        # -grab
        if not video_capture.grab():
            return FramePayload(False, None, None)

        timestamp_ns_post_grab = time.time_ns()
        timestamp_ns = (timestamp_ns_pre_grab + timestamp_ns_post_grab) / 2

        success, image = video_capture.retrieve()
        return FramePayload(success, image, timestamp_ns)
