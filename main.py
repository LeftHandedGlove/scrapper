import numpy as np
import cv2

import pyautogui
import pygetwindow
import time
import math
import multiprocessing

from image_grabber import ImageGrabber
from status_manager import StatusManager






def move_mouse_to_default_position(window_handle: pygetwindow.Win32Window) -> None:
    mouse_pos_x = int(window_handle.width / 2)
    mouse_pos_y = int((window_handle.height / 2) - ((window_handle.height / 20)))
    pyautogui.moveTo(mouse_pos_x, mouse_pos_y)

def resize_image(image: np.ndarray, amount: float) -> np.ndarray:
    scale_percent = int(100 * amount)
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_img = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized_img

def rotateCam(degrees: float):
    if degrees == 0 :
        return
    # Get the key to press based on the direction
    left_dir_key = "."
    right_dir_key = ","
    key = left_dir_key if degrees > 0 else right_dir_key
    # Map the degrees to a time
    abs_degrees = abs(round(degrees, 2))
    degree_time_map = {     # Tested manually, not perfect but close
        360: 3.95,
        180: 1.9,
        90: 0.91,
        45: 0.4,
        22.5: 0.13,
        10: 0.0
    }
    try:
        time_to_sleep = degree_time_map[abs_degrees]
    except KeyError:
        print(f"{degrees} is an invalid value for rotation.")
        return False
    pyautogui.keyDown(key)
    time.sleep(time_to_sleep)
    pyautogui.keyUp(key)
    return True



def rotate_camera_to_direction(direction: int) -> None:
    compass_image = extract_compass_from_image()
    current_direction = get_camera_compass_direction()



def main():
    foxhole_window = pygetwindow.getWindowsWithTitle('War')[0]
    move_mouse_to_default_position(foxhole_window)
    pyautogui.click()
    with multiprocessing.Manager() as shared_info_manager:
        shared_image_list = shared_info_manager.list()
        shared_status_dict = shared_info_manager.dict()
        image_grab = ImageGrabber(shared_image_list, 'War')
        image_grab.start()
        status_manager = StatusManager(shared_image_list, shared_status_dict)
        status_manager.start()
        while True:
            try:
                src_img = shared_image_list[0]
                resized_img = resize_image(src_img, 0.5)
                cv2.imshow('raw_data_50%', resized_img)
            except:
                pass
            move_mouse_to_default_position(foxhole_window)

            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                cv2.destroyAllWindows()
                break

if __name__ == '__main__':
    main()