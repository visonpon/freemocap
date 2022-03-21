import cv2

from src.cameras.capture.opencv_camera.opencv_camera import OpenCVCamera
from src.cameras.capture.opencv_camera.webcam_config import WebcamConfig

cam1 = OpenCVCamera(
    config=WebcamConfig(webcam_id=0),
    as_process=True,
)
cam1.start_frame_capture()

print("Started")

while True:
    cv2.imshow("test", cam1.latest_frame)
    print(f"FPS {cam1.current_fps}")
    exit_key = cv2.waitKey(1)
    if exit_key == 27:
        break

cv2.destroyAllWindows()
