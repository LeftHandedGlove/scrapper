import multiprocessing
import time
import math
import pygetwindow
import numpy as np
import cv2

class StatusManager(multiprocessing.Process):
    def __init__(self, shared_image_list: list, shared_status_dict: dict):
        self.shared_image_list = shared_image_list
        self.shared_status_dict = shared_status_dict

    def run(self):
        next_run_time = 0
        period = 0.2
        while True:
            if time.time() > next_run_time:
                next_run_time = next_run_time + period

    def extract_compass_from_image(window_handle: pygetwindow.Win32Window, image: np.ndarray) -> np.ndarray:
        top = 33
        height = 112
        left = 1774
        width = 112
        compass_image = image[top:top+height, left:left+width]
        return compass_image

    def get_camera_compass_direction(compass_image: np.ndarray) -> int:
        # Threshold of the orange in the N
        compass_image_hsv = cv2.cvtColor(compass_image, cv2.COLOR_BGR2HSV)
        n_h = 10
        n_s = 176
        n_v = 230
        threshold = 15
        only_n_image = cv2.inRange(
            compass_image_hsv, 
            (n_h - threshold, n_s - threshold, n_v - threshold), 
            (n_h + threshold, n_s + threshold, n_v + threshold)
        )
        contours,hierarchy = cv2.findContours(only_n_image, 1, 2)
        try:
            cnt = contours[0]
            M = cv2.moments(cnt)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            img_mid_height = int(only_n_image.shape[0] / 2)
            img_mid_width = int(only_n_image.shape[1] / 2)
            cv2.drawContours(only_n_image, [cnt], -1, 125, 2)
            cv2.line(only_n_image, (img_mid_width, img_mid_height), (cx, cy), 255, 1)
            # This is flipped because we went from top-left origin to bottom-left origin
            opposite = img_mid_height - cy
            adjacent = cx - img_mid_width
            if opposite > 0 and adjacent == 0:  # Straight North
                direction = 0
            elif opposite > 0  and adjacent > 0:  # North West
                direction = 270 + math.degrees(math.atan(opposite / adjacent))
            elif opposite == 0 and adjacent > 0:  # Straight West
                direction = 270
            elif opposite < 0  and adjacent > 0:  # South West
                direction = 270 + math.degrees(math.atan(opposite / adjacent))
            elif opposite < 0 and adjacent == 0:  # Straight South
                direction = 180
            elif opposite < 0  and adjacent < 0:  # South East
                direction = 90 + math.degrees(math.atan(opposite / adjacent))
            elif opposite == 0 and adjacent < 0:  # Straight East
                direction = 90
            elif opposite > 0  and adjacent < 0:  # North East
                direction = 90 + math.degrees(math.atan(opposite / adjacent))
            direction = round(direction)
            print(direction)
        except Exception:
            pass
        return only_n_image
            

