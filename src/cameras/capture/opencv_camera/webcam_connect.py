import logging
import platform

import cv2

from src.cameras.capture.opencv_camera.webcam_config import WebcamConfig

logger = logging.getLogger(__name__)


class VideoCaptureFactory:
    def create(self, config: WebcamConfig):
        if platform.system() == "Windows":
            cap_backend = cv2.CAP_DSHOW
        else:
            cap_backend = cv2.CAP_ANY

        try:
            webcam_id = int(config.webcam_id)
        except:
            webcam_id = config.webcam_id

        video_capture = cv2.VideoCapture(webcam_id, cap_backend)

        if not video_capture:
            raise RuntimeError(
                f"Video capture object failed to initialize for webcam_id: {config.webcam_id}"
            )

        success, image = video_capture.read()

        if not success:
            logger.error(
                "Could not connect to a camera at port# {}".format(config.webcam_id)
            )
            return success
        logger.debug(f"Camera found at port number {config.webcam_id}")
        fps_input_stream = int(video_capture.get(5))
        logger.debug("FPS of webcam hardware/input stream: {}".format(fps_input_stream))
        return video_capture

    def _apply_configuration(self, video_capture, config):
        # set camera stream parameters
        video_capture.set(cv2.CAP_PROP_EXPOSURE, config.exposure)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.resolution_width)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.resolution_height)
        video_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*config.fourcc))
