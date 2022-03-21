import logging
import threading
import time
import traceback
from multiprocessing import Process
from multiprocessing.connection import Pipe
from threading import Thread
from typing import Optional

from src.cameras.capture.opencv_camera.frame_thread import FrameCapture
from src.cameras.capture.opencv_camera.webcam_config import WebcamConfig
from src.cameras.capture.opencv_camera.webcam_connect import VideoCaptureFactory

logger = logging.getLogger(__name__)


class CamProcessHandler:
    def __init__(self, config: WebcamConfig):
        self.is_capturing_frames = False
        self._config = config
        self._process: Optional[Process] = None
        self.image_reader, self.image_writer = Pipe()
        self.fps_reader, self.fps_writer = Pipe()

    def _start(self, iw, fps):
        fc = FrameCapture(
            config=self._config,
            image_writer=iw,
            fps_writer=fps,
        )
        fc.run()

    def start_frame_capture(self, join=False):
        self._process = Process(
            target=self._start, args=(self.image_writer, self.fps_writer), daemon=True
        )
        self._process.start()
        if join:
            self._process.join()

    @property
    def latest_frame(self):
        return self.image_reader.recv()

    @property
    def current_fps(self):
        return self.fps_reader.recv()

    @property
    def session_writer_path(self):
        return ""

    def close(self):
        try:
            self._process.terminate()
            while self._process.is_alive():
                # wait for process to die.
                time.sleep(0.1)
        except:
            logger.error("Printing traceback")
            traceback.print_exc()
        finally:
            logger.info("Closed Camera {}".format(self._config.webcam_id))


class CamThreadHandler:
    def __init__(self, config: WebcamConfig):
        self._config = config
        self.is_capturing_frames = (False,)
        self._thread: threading.Thread = None
        c = VideoCaptureFactory()
        self._video_capture = c.create(WebcamConfig(webcam_id=self._config.webcam_id))
        self._fc = FrameCapture(
            video_capture=self._video_capture,
            save_video=config.save_video,
            webcam_id=config.webcam_id,
        )

    def start_frame_capture(self, join=False):
        self._thread = Thread(target=self._fc.run, daemon=True)
        self._thread.start()
        self.is_capturing_frames = True
        if join:
            self._thread.join()

    @property
    def latest_frame(self):
        return self._fc.latest_frame

    @property
    def current_fps(self):
        return self._fc.current_fps

    @property
    def session_writer_path(self):
        return self._fc.session_writer_path

    def close(self):
        try:
            self._fc.stop()
            while self._thread.is_alive():
                # wait for thread to die.
                # TODO: use threading.Event for synchronize mainthread vs other threads
                time.sleep(0.1)
        except:
            logger.error("Printing traceback")
            traceback.print_exc()
        finally:
            logger.info("Closed Camera {}".format(self._config.webcam_id))


class OpenCVCamera:
    """
    OpenCV Camera implementation with native threading or process handling
    """

    def __init__(
        self,
        config: WebcamConfig,
        as_process: bool = True,
    ):
        self._config = config
        self._name = f"Camera {self._config.webcam_id}"
        if as_process:
            self._capture_handler = CamProcessHandler(self._config)
        else:
            self._capture_handler = CamThreadHandler(self._config)

    @property
    def webcam_id_as_str(self):
        return str(self._config.webcam_id)

    @property
    def current_fps(self):
        return self._capture_handler.current_fps

    @property
    def is_capturing_frames(self):
        if not self._capture_handler.is_capturing_frames:
            logger.error("Frame Capture not running yet")
            return False

        return self._capture_handler.is_capturing_frames

    @property
    def current_fps_short(self) -> str:
        return "{:.2f}".format(self._capture_handler.current_fps)

    @property
    def latest_frame(self):
        return self._capture_handler.latest_frame

    @property
    def session_writer_base_path(self):
        return ""

    def start_frame_capture(self):
        if self.is_capturing_frames:
            logger.debug(
                f"Already capturing frames for webcam_id: {self.webcam_id_as_str}"
            )
            return
        logger.info(
            f"Beginning frame capture thread for webcam: {self.webcam_id_as_str}"
        )
        self._capture_handler.start_frame_capture()

    def stop_frame_capture(self):
        self.close()

    def close(self):
        self._capture_handler.close()
