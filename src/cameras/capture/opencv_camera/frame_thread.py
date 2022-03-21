import logging
import traceback
from multiprocessing.connection import Connection
from pathlib import Path

import cv2

from src.cameras.capture.frame_payload import FramePayload
from src.cameras.capture.opencv_camera.frame_grabber import FrameGrabber
from src.cameras.capture.opencv_camera.webcam_config import WebcamConfig
from src.cameras.capture.opencv_camera.webcam_connect import VideoCaptureFactory
from src.cameras.persistence.video_writer.save_options import SaveOptions
from src.cameras.persistence.video_writer.video_writer import VideoWriter
from src.core_processor.fps.fps_counter import FPSCounter

logger = logging.getLogger(__name__)


class FrameCapture:
    def __init__(
        self,
        config: WebcamConfig,
        session_writer_path=None,
        video_capture: cv2.VideoCapture = None,
        image_writer: Connection = None,
        fps_writer: Connection = None,
    ):
        self._is_capturing_frames = False
        self._video_capture = video_capture
        self._webcam_id = config.webcam_id
        self._save_video = config.save_video
        self._config = config
        self._num_frames_processed = 0
        self._elapsed = 0
        self._frame: FramePayload = FramePayload()
        self._image_writer = image_writer
        c = VideoCaptureFactory()
        self._video_capture = c.create(self._config)
        self.session_writer_path = session_writer_path
        self._fps_counter = FPSCounter()
        self._fps_writer = fps_writer

    @property
    def current_fps(self):
        return self._fps_counter.current_fps

    @property
    def frame_width(self):
        return int(self._video_capture.get(3))

    @property
    def frame_height(self):
        return int(self._video_capture.get(4))

    @property
    def latest_frame(self):
        return self._frame

    @property
    def is_capturing_frames(self):
        return self._is_capturing_frames

    def stop(self):
        if not self._video_capture:
            return

        self._is_capturing_frames = False
        self._video_capture.release()

    def run(self, session_path: Path):
        self._start_frame_loop(session_path)

    def _start_frame_loop(self, session_path: Path):
        video_writer = VideoWriter()
        self._is_capturing_frames = True

        try:
            while self._is_capturing_frames:
                frame = FrameGrabber.get(self._video_capture)
                self._fps_counter.increment(frame)
                self._frame = frame
                if self._image_writer:
                    self._image_writer.send(frame)
                if self._fps_writer:
                    self._fps_writer.send(self._fps_counter.current_fps)
                if self._config.save_video:
                    video_writer.write(frame)
        except:
            logger.error("Frame loop thread exited due to error")
            traceback.print_exc()
        else:
            logger.info("Frame loop thread exited.")
        finally:
            if not self._config.save_video:
                return
            options = SaveOptions(
                writer_dir=Path().joinpath(
                    session_path,
                    "raw_frame_capture",
                    f"webcam_{self._webcam_id}",
                ),
                fps=self._fps_counter.current_fps,
                frame_width=self.frame_width,
                frame_height=self.frame_height,
            )
            video_writer.save(options)
