import numpy as np
import cv2
import os
from numpy.lib.polynomial import polysub
import pyautogui
import pygetwindow
import time
import math
from mss import mss

foxhole_window = pygetwindow.getWindowsWithTitle('War')[0]
sct = mss()
bounding_box = {
    'top': foxhole_window.top, 
    'left': foxhole_window.left, 
    'width': foxhole_window.width, 
    'height': foxhole_window.height
}
src_image = None

def grab_new_frame():
    global sct
    global bounding_box
    global src_image
    src_image = np.array(sct.grab(bounding_box))

def extract_grey_threshold_image(image, top, height, left, width, threshold):
    extracted_image = image[top:top+height, left:left+width]
    grey_image = cv2.cvtColor(extracted_image, cv2.COLOR_BGR2GRAY)
    ret,thresh_image = cv2.threshold(grey_image, threshold, 255, cv2.THRESH_BINARY)
    return thresh_image

def get_diff_between_images(image1, image2):
    xor_image = cv2.bitwise_xor(image1, image2)
    avg_value= cv2.mean(xor_image)
    return avg_value

def verify_image_in_image(small_image, big_image, threshold=0.2):
    result = cv2.matchTemplate(big_image, small_image, cv2.TM_SQDIFF_NORMED)
    return result[0][0] < threshold
    
def verify_mouse_in_window():
    good_horz = foxhole_window.left <= pyautogui.position().x <= foxhole_window.left + foxhole_window.width
    good_vert = foxhole_window.top <= pyautogui.position().y <= foxhole_window.top + foxhole_window.height
    return (good_vert and good_horz)

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

def rotate_cam(degrees: float):
    open_close_character_inventory(should_be_open=False)
    # Get the key to press based on the direction
    left_dir_key = "."
    right_dir_key = ","
    key = right_dir_key if degrees > 0 else left_dir_key
    # Calculate the time to hold the button
    abs_degrees = abs(degrees)
    if abs_degrees < 7:
        return False
    time_to_sleep = max((0.0112 * abs_degrees) - 0.111, 0)
    if verify_mouse_in_window():
        pyautogui.keyDown(key)
        time.sleep(time_to_sleep)
        pyautogui.keyUp(key)
        time.sleep(0.5)
        return True

def get_camera_compass_direction() -> int:
    open_close_character_inventory(should_be_open=False)
    global src_image
    top = 33
    height = 112
    left = 1774
    width = 112
    compass_image = src_image[top:top+height, left:left+width]
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
        # cv2.drawContours(only_n_image, [cnt], -1, 125, 2)
        # cv2.line(only_n_image, (img_mid_width, img_mid_height), (cx, cy), 255, 1)
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
    except Exception:
        return -1
    return direction

def rotate_camera_to_direction(desired_direction: int) -> bool:
    open_close_character_inventory(should_be_open=False)
    while True:
        current_direction = get_camera_compass_direction()
        if current_direction == -1:
            return False
        delta_angle = desired_direction - current_direction
        if delta_angle < -180:
            delta_angle += 360
        if not rotate_cam(delta_angle):
            break
        else:
            grab_new_frame()

    return True

def move_player(direction: str, distance: int):
    open_close_character_inventory(should_be_open=False)
    direction_keys_map = {
        "UP": ["w"],
        "UP-RIGHT": ["w", "d"],
        "RIGHT": ["d"],
        "DOWN-RIGHT": ["s", "d"],
        "DOWN": ["s"],
        "DOWN-LEFT": ["s", "a"],
        "LEFT": ["a"],
        "UP-LEFT": ["w", "a"]
    }
    if verify_mouse_in_window():
        for key in direction_keys_map[direction]:
            pyautogui.keyDown(key)
        time.sleep(0.1 * distance)
        for key in direction_keys_map[direction]:
            pyautogui.keyUp(key)

def get_wielded_item() -> str:
    open_close_character_inventory(should_be_open=False)
    grab_new_frame()
    global src_image
    current_item_icon_thresh_image = extract_grey_threshold_image(image=src_image.copy(),top=20, height=68, left=20, width=68, threshold=150)
    wielded_item = "unknown"
    for item_path in os.listdir('wielded_images'):
        if 'text' in item_path:
            continue
        current_icon_image = cv2.imread(os.path.join('wielded_images', item_path), cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(current_icon_image, current_item_icon_thresh_image, cv2.TM_SQDIFF_NORMED)
        if result[0][0] < 0.2:
            wielded_item = os.path.splitext(item_path)[0]
    if wielded_item == 'hammer':
        top = 95
        height = 19
        left = 20
        width = 250
        current_item_text_image = src_image[top:top+height, left:left+width]
        ret,current_item_text_thresh_image = cv2.threshold(current_item_text_image,150,255,cv2.THRESH_BINARY)
        current_item_text_thresh_grey_image = cv2.cvtColor(current_item_text_thresh_image, cv2.COLOR_BGR2GRAY)
        hammer_build_text_image = cv2.imread(os.path.join('wielded_images', 'hammer_build_text.png'), cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(hammer_build_text_image, current_item_text_thresh_grey_image, cv2.TM_SQDIFF_NORMED)
        if result[0][0] < 0.2:
            wielded_item += "_build"
        hammer_upgrade_text_image = cv2.imread(os.path.join('wielded_images', 'hammer_upgrade_text.png'), cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(hammer_upgrade_text_image, current_item_text_thresh_grey_image, cv2.TM_SQDIFF_NORMED)
        if result[0][0] < 0.2:
            wielded_item += "_upgrade"
        cv2.imshow('current item text', current_item_text_thresh_image)
    cv2.imshow('current item icon', current_item_icon_thresh_image)
    print(wielded_item)
    return wielded_item

def open_close_character_inventory(should_be_open):
    global src_image
    while True:
        # Check the center of the screen for the equipment text
        only_char_invent_title_thresh_image = extract_grey_threshold_image(image=src_image.copy(), top=150, height=30, left=780, width=100, threshold=150)
        only_char_invent_title_compare_image = cv2.imread(os.path.join('inventory_images', 'equipment_text.png'), cv2.IMREAD_GRAYSCALE)
        currently_open = verify_image_in_image(
            small_image=only_char_invent_title_compare_image, 
            big_image=only_char_invent_title_thresh_image
        )
        if (currently_open and not should_be_open) or (not currently_open and should_be_open):
            if verify_mouse_in_window():
                pyautogui.press('\t')
            time.sleep(0.5)
            grab_new_frame()
        else:
            break

def get_equipment() -> dict:
    open_close_character_inventory(should_be_open=True)
    grab_new_frame()
    coords_dict = {
        "Primary": (184, 67, 782, 67),
        "Secondary": (256, 67, 782, 67),
        "Tertiary": (328, 67, 782, 67),
        "Radio": (328, 67, 998, 67),
        "Gas Mask": (184, 67, 1070, 67),
        "Radio Backpack": (256, 67, 1070, 67),
        "Weapon Attachment": (328, 67, 1070, 67),
        "Large Item": (184, 67, 854, 67)
    }
    equipment_dict = coords_dict.copy()
    for slot_name, image_coords in coords_dict.items():
        thresh_image = extract_grey_threshold_image(
            image=src_image.copy(), 
            top=image_coords[0], 
            height=image_coords[1], 
            left=image_coords[2], 
            width=image_coords[3],
            threshold=150
        )
        for item_path in os.listdir('inventory_images'):
            if 'text' in item_path:
                continue
            current_icon_image = cv2.imread(os.path.join('inventory_images', item_path), cv2.IMREAD_GRAYSCALE)
            result = cv2.matchTemplate(current_icon_image, thresh_image, cv2.TM_SQDIFF_NORMED)
            if result[0][0] < 0.2:
                equipment_dict[slot_name] = os.path.splitext(item_path)[0]
                break
            else:
                equipment_dict[slot_name] = "unknown"
    return equipment_dict

def get_backpack():
    open_close_character_inventory(should_be_open=True)
    grab_new_frame()
    coords_list = [
        (438, 67, 782, 67),
        (438, 67, 854, 67),
        (438, 67, 926, 67),
        (438, 67, 998, 67),
        (438, 67, 1070, 67),
        (510, 67, 782, 67),
        (510, 67, 854, 67),
        (510, 67, 926, 67),
        (510, 67, 998, 67),
    ]
    backpack_list = ["unknown"] * len(coords_list)
    for index, image_coords in enumerate(coords_list):
        thresh_image = extract_grey_threshold_image(
            image=src_image.copy(), 
            top=image_coords[0], 
            height=image_coords[1], 
            left=image_coords[2], 
            width=image_coords[3],
            threshold=150
        )
        for item_path in os.listdir('inventory_images'):
            if 'text' in item_path:
                continue
            current_icon_image = cv2.imread(os.path.join('inventory_images', item_path), cv2.IMREAD_GRAYSCALE)
            result = cv2.matchTemplate(current_icon_image, thresh_image, cv2.TM_SQDIFF_NORMED)
            if result[0][0] < 0.2:
                backpack_list[index] = os.path.splitext(item_path)[0]
                break
    return(backpack_list)

def wield_item(desired_item: str) -> bool:
    # Check if we're already wielding it
    if desired_item in get_wielded_item():
        return True
    # If not then check if we have it equipped and wield it
    else:
        if equip_item(desired_item):
            for slot_name, item_name in get_equipment().items():
                if item_name == desired_item:
                    wield_slot(slot_name)
                    return True
        # If the equip failed then we don't have the item
        else:
            return False

def wield_slot(slot_name: str) -> bool:
    open_close_character_inventory(should_be_open=False)
    if slot_name == 'Primary':
        key = '1'
    elif slot_name == 'Secondary':
        key = '2'
    elif slot_name == 'Tertiary':
        key = '3'
    else:
        return False
    if verify_mouse_in_window():
        pyautogui.press(key)
        return True
    return False

def equip_item(desired_item: str) -> bool:
    open_close_character_inventory(should_be_open=True)
    click_coords = [
        (438 + 33, 782 + 33),
        (438 + 33, 854 + 33),
        (438 + 33, 926 + 33),
        (438 + 33, 998 + 33),
        (438 + 33, 1070 + 33),
        (510 + 33, 782 + 33),
        (510 + 33, 854 + 33),
        (510 + 33, 926 + 33),
        (510 + 33, 998 + 33)
    ]
    for slot_name, item_name in get_equipment().items():
        if item_name == desired_item:
            return True
    current_backpack = get_backpack()
    try:
        desired_item_index = current_backpack.index(desired_item)
        if verify_mouse_in_window():
            pyautogui.click(
                x=click_coords[desired_item_index][1],
                y=click_coords[desired_item_index][0]
            )
            return True
        else:
            return False
    except ValueError:
        return False
    

def main():
    foxhole_window.activate()
    move_mouse_to_default_position(foxhole_window)
    pyautogui.click()
    grab_new_frame()
    rotate_camera_to_direction(0)
    global src_image
    while True:
        try:
            grab_new_frame()
            resized_img = resize_image(src_image.copy(), 0.5)
            cv2.imshow('raw_data_50%', resized_img)
        except KeyboardInterrupt:
            break
        except Exception as err:
            print(err)
        # move_mouse_to_default_position(foxhole_window)
        rotate_camera_to_direction(0)
        print(wield_item('hammer'))

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            cv2.destroyAllWindows()
            break

if __name__ == '__main__':
    main()