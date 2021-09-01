import multiprocessing
import time
from mss import mss
import pygetwindow
import numpy as np

class ImageGrabber(multiprocessing.Process):
    def __init__(self, shared_image_list: list, window_name: str):
        super().__init__()
        self.daemon = True
        self.shared_image_list = shared_image_list
        shared_image_list.append(None)
        self.window_name = window_name

    def run(self):
        self.window_handle = pygetwindow.getWindowsWithTitle(self.window_name)[0]
        sct = mss()
        bounding_box = {
            'top': self.window_handle.top, 
            'left': self.window_handle.left, 
            'width': self.window_handle.width, 
            'height': self.window_handle.height
        }
        while True:
            image = np.array(sct.grab(bounding_box))
            self.shared_image_list[0] = image
