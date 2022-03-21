import cv2

from src.cameras.capture.opencv_camera.opencv_camera import OpenCVCamera
from src.cameras.capture.opencv_camera.webcam_config import WebcamConfig
from src.utils.time_str import create_session_path

cam1 = OpenCVCamera(
    config=WebcamConfig(webcam_id=0),
    as_process=True,
)
cam1.start_frame_capture(create_session_path())

print("Started")

while True:
    cv2.imshow("test", cam1.latest_frame)
    exit_key = cv2.waitKey(1)
    if exit_key == 27:
        break

cv2.destroyAllWindows()
