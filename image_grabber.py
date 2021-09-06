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
        pass