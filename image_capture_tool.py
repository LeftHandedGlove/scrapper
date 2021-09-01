# https://www.codeproject.com/Articles/5270236/Installing-OpenCV-and-ImageAI-for-Object-Detection

import numpy as np
import cv2
from mss import mss
from PIL import Image
import pyautogui
import pygetwindow
import win32gui


screen_height = pyautogui.size().height
screen_width = pyautogui.size().width

foxhole_window = pygetwindow.getWindowsWithTitle('War')[0]

bounding_box = {
    'top': foxhole_window.top, 
    'left': foxhole_window.left, 
    'width': foxhole_window.width, 
    'height': foxhole_window.height
}

sct = mss()

foxhole_window = pygetwindow.getWindowsWithTitle('War')[0]
foxhole_window.activate()
# foxhole_window.moveTo(-7, 0)
# foxhole_window.resizeTo(int(screen_width / 2), int(screen_height / 2))

mouse_pos_x = int(foxhole_window.width / 2)
mouse_pos_y = int((foxhole_window.height / 2) - ((foxhole_window.height / 20)))
pyautogui.moveTo(mouse_pos_x, mouse_pos_y)

player_box_left = int((foxhole_window.width / 2) - (foxhole_window.width / 15))
player_box_top = int((foxhole_window.height / 2) - (foxhole_window.height / 9))
player_box_right = int((foxhole_window.width / 2) + (foxhole_window.width / 15))
player_box_bottom = int((foxhole_window.height / 2) + (foxhole_window.height / 10))


while True:
    src_img = np.array(sct.grab(bounding_box))
    scale_percent = 50
    width = int(src_img.shape[1] * scale_percent / 100)
    height = int(src_img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_img = cv2.resize(src_img, dim, interpolation=cv2.INTER_AREA)
    cv2.imshow('blue', resized_img)

    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        cv2.destroyAllWindows()
        break

def find_scrap(grey_img):
    pass