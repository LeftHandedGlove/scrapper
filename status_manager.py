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

    
            

