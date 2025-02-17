import math
import os
import glob
import sys

from utils.files.fileWriter import FileWriter
from utils.grabbers.mss import Grabber
from utils.fps import FPS

# computer vision (OpenCV)
import cv2

import numpy as np
from utils.nms import non_max_suppression_fast
from utils.cv2 import filter_rectangles

from utils.controls.mouse.win32 import MouseControls
from utils.win32 import WinHelper
import keyboard
from termcolor import colored
import time
from utils.time import sleep
from ConfigReader import ConfigReader
from screen_to_world import get_move_angle, get_move_angle_my
import os
config_path = r"./config.ini"

if os.path.exists(config_path):
    print(f"Config file found at {config_path}")
else:
    print(f"Config file not found at {config_path}")
config_reader = ConfigReader('config.ini')
print(colored('''
                     
░█████╗░██╗███╗░░░███╗██╗░░░░░░█████╗░██████╗░██████╗░░█████╗░████████╗
██╔══██╗██║████╗░████║██║░░░░░██╔══██╗██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝
███████║██║██╔████╔██║██║░░░░░███████║██████╦╝██████╦╝██║░░██║░░░██║░░░
██╔══██║██║██║╚██╔╝██║██║░░░░░██╔══██║██╔══██╗██╔══██╗██║░░██║░░░██║░░░
██║░░██║██║██║░╚═╝░██║███████╗██║░░██║██████╦╝██████╦╝╚█████╔╝░░░██║░░░
╚═╝░░╚═╝╚═╝╚═╝░░░░░╚═╝╚══════╝╚═╝░░╚═╝╚═════╝░╚═════╝░░╚════╝░░░░╚═╝░░░                                                                         
                                             AIMLAB COLOR AIMBOT - v1.0''', 'magenta'))
print()
print(colored('[Info]', 'green'), colored('Made By', 'white'), colored('Alexyei', 'magenta'))
print(colored('[Info]', 'green'), colored('Packed By', 'white'), colored('VGlalala', 'magenta'))
print(colored('[Info]', 'green'), colored('QQ', 'white'), colored('237441767', 'magenta'))
print(colored('[Info]', 'green'), colored('Discord', 'white'), colored('vglalala', 'magenta'))
# Assign config values
ACTIVATION_HOTKEY = config_reader.activation_hotkey
EXIT_HOTKEY = config_reader.exit_hotkey
MOVELEFT_HOTKEY = config_reader.moveleft_hotkey
MOVERIGHT_HOTKEY = config_reader.moveright_hotkey
MOVEUP_HOTKEY = config_reader.moveup_hotkey
MOVEDOWN_HOTKEY = config_reader.movedown_hotkey
AUTO_DEACTIVATE_AFTER = config_reader.auto_deactivate_after
SCREENSHOTS_FOLDER = config_reader.screenshots_folder
_shoot = config_reader.shoot
_show_cv2 = config_reader.show_cv2
_write_cv2 = config_reader.write_cv2
_show_fps = config_reader.show_fps

_pause = config_reader.pause
_shoot_interval = config_reader.shoot_interval

game_window_rect = WinHelper.GetWindowRect("aimlab_tb", (8, 30, 16, 38))
_ret = config_reader.ret
_aim = config_reader.aim
_activation_time = config_reader.activation_time

# # config
# # Push CAPS-LOOK for run bot
# # https://snipp.ru/handbk/scan-codes
# ACTIVATION_HOTKEY = 58  # 58 = CAPS-LOCK
# EXIT_HOTKEY = 69  # Escape
# MOVELEFT_HOTKEY = 75
# MOVERIGHT_HOTKEY = 77
# MOVEUP_HOTKEY = 72
# MOVEDOWN_HOTKEY = 80
# AUTO_DEACTIVATE_AFTER = 62  # seconds or None (default Aim Lab map time is 60 seconds)
# SCREENSHOTS_FOLDER = r"./screenshots"
# # always True
# _shoot = True
# # show rectangles for sphere online
# _show_cv2 = False
# _write_cv2 = False
# _show_fps = False
#
# # the bigger these values, the more accurate and fail-safe bot will behave
# # minimum interval after move hover to target
# # PAUSE BEFORE SHOT
# _pause = 0.02
# # minimum interval between shoots
# _shoot_interval = 0.02  # seconds
#
# # used by the script
# # left, top, width, height
# # in windows we have shadow for window 8 pixel for each side
# # location +8 + 30 size -16 -38 - 8
# # 22+8 (header +shadow)
  # cut the borders
# print(game_window_rect)
# _ret = None
#
# # shoot mode now or not
# _aim = False
# # start shoot mode time
# _activation_time = 0


# clear scrennshoots
files = glob.glob(f'{SCREENSHOTS_FOLDER}/*')
for f in files:
    os.remove(f)


def cv2_process():
    global _aim, _shoot, _ret, _pause, _shoot_interval, _show_cv2, _write_cv2, _show_fps, game_window_rect, _activation_time

    fps = FPS()
    font = cv2.FONT_HERSHEY_SIMPLEX
    _last_shoot = None
    grabber = Grabber()

    mouse = MouseControls()

    mistake_movies = 0
    # angle of view
    fov = [106.26, 73.74, 113.66]  # horizontal, vertical, depth

    x360 = 8182 * 2  # x value to rotate on 360 degrees
    x1 = x360 / 360

    # if we target ball, ball on center screnn, cut 6x6 square on center, if hue color we target right
    def check_dot(hue_point):

        dot_img = grabber.get_image({"left": game_window_rect[0] + (game_window_rect[2] // 2) - 3,
                                     "top":
                                         game_window_rect[1] + (game_window_rect[3] // 2) - 3,
                                     "width": 6,
                                     "height": 6})

        dot_img = cv2.cvtColor(dot_img, cv2.COLOR_BGR2HSV)
        # print(dot_img)
        avg_color_per_row = np.average(dot_img, axis=0)
        # print(avg_color_per_row)
        avg_color = np.average(avg_color_per_row, axis=0)
        # print("AVG COLOR: ", avg_color, " hue: ", hue_point)
        # print(hue_point - 10 < avg_color[0] < hue_point + 20)

        return (hue_point - 10 < avg_color[0] < hue_point + 20) and (avg_color[1] > 120) and (avg_color[2] > 100)

    while True:
        # if we have screenshots
        img = grabber.get_image(
            {"left": int(game_window_rect[0]), "top": int(game_window_rect[1]), "width": int(game_window_rect[2]),
             "height": int(game_window_rect[3])})
        if img is None:
            continue

        img_time = time.time()

        # some processing code
        # OpenCV HSV Scale (H: 0-179, S: 0-255, V: 0-255)
        hue_point = 87
        sphere_color = ((hue_point, 100, 100), (hue_point + 20, 255, 255))  # HSV
        min_target_size = (10, 10)
        max_target_size = (150, 150)

        # convert bgr to hsv image
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # create mask from color to color
        mask = cv2.inRange(hsv, np.array(sphere_color[0], dtype=np.uint8),
                           np.array(sphere_color[1], dtype=np.uint8))

        if _write_cv2:
            FileWriter.write_img(mask, rf"{SCREENSHOTS_FOLDER}\{img_time}_2_mask.jpg")

        # https://robotclass.ru/tutorials/opencv-python-find-contours/
        # https://medium.com/analytics-vidhya/opencv-findcontours-detailed-guide-692ee19eeb18
        #
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        rectangles = []

        for cnt in contours:
            # wrap contour to rectangle
            x, y, w, h = cv2.boundingRect(cnt)
            if (w >= min_target_size[0] and h >= min_target_size[1]) \
                    and (w <= max_target_size[0] and h <= max_target_size[1]):
                rectangles.append((int(x), int(y), int(w), int(h)))

        # if not rectangles go to next screenshot
        if not rectangles:
            continue

        if _show_cv2:
            for idx, rect in enumerate(rectangles):
                # print(idx)
                x, y, w, h = rect
                cv2.rectangle(img, (x, y), (x + w, y + h), [255, 0, 0], 6)
                img = cv2.putText(img, f"{(x + w, y + h)}", (x, y - 10), font,
                                  .5, (0, 255, 0), 1, cv2.LINE_AA)
        if _write_cv2:
            FileWriter.write_img(img, rf"{SCREENSHOTS_FOLDER}\{img_time}_3_img.jpg")

        # union near contours
        # Apply NMS
        rectangles = np.array(non_max_suppression_fast(np.array(rectangles), overlapThresh=0.3))

        # Filter rectangles (join intersections)
        rectangles = filter_rectangles(rectangles.tolist())

        # detect closest target
        closest = 1000000
        aim_rect = None
        for rect in rectangles:
            x, y, w, h = rect
            mid_x = int((x + (x + w)) / 2)
            mid_y = int((y + (y + h)) / 2)
            dist = math.dist([game_window_rect[2] // 2, game_window_rect[3] // 2], [mid_x, mid_y])

            if dist < closest:
                closest = dist
                aim_rect = rect

        x, y, w, h = aim_rect
        if _show_cv2:
            # draw rectangle
            cv2.rectangle(img, (x, y), (x + w, y + h), [0, 255, 0], 2)

        # shoot
        mid_x = int((x + (x + w)) / 2)
        mid_y = int((y + (y + h)) / 2)
        # -1 fill circle
        if _show_cv2:
            cv2.circle(img, (mid_x, mid_y), 10, (0, 0, 255), -1)

        if _write_cv2:
            FileWriter.write_img(img, rf"{SCREENSHOTS_FOLDER}\{img_time}_4_dot.jpg")
        if _aim:
            if _last_shoot is None or time.perf_counter() > (_last_shoot + _shoot_interval):
                if _show_cv2:
                    game_window_rect__center = (game_window_rect[2] // 2, game_window_rect[3] // 2)
                    # print(game_window_rect__center)
                    cv2.circle(img, game_window_rect__center, 10, (0, 255, 255), -1)
                if _write_cv2:
                    FileWriter.write_img(img, rf"{SCREENSHOTS_FOLDER}\{img_time}_5_center.jpg")

                # rel_diff = get_move_angle((mid_x, mid_y), game_window_rect, x1, fov)
                rel_diff = get_move_angle_my((mid_x, mid_y), game_window_rect, x1, fov)

                # move the mouse
                mouse.move_relative(int(rel_diff[0]), int(rel_diff[1]))

                sleep(_pause)

                if _show_cv2:
                    img = grabber.get_image(
                        {"left": int(game_window_rect[0]), "top": int(game_window_rect[1]),
                         "width": int(game_window_rect[2]),
                         "height": int(game_window_rect[3])})
                    game_window_rect__center = (game_window_rect[2] // 2, game_window_rect[3] // 2)
                    # print(game_window_rect__center)
                    cv2.circle(img, game_window_rect__center, 5, (255, 255, 0), -1)
                if _write_cv2:
                    img = grabber.get_image(
                        {"left": int(game_window_rect[0]), "top": int(game_window_rect[1]),
                         "width": int(game_window_rect[2]),
                         "height": int(game_window_rect[3])})
                    FileWriter.write_img(img, rf"{SCREENSHOTS_FOLDER}\{img_time}_6_moved.jpg")

                print("moved")
                if _shoot:
                    # detect if aiming the target (more accurate)

                    if _write_cv2:
                        dot_img = grabber.get_image(
                            {"left": game_window_rect[0] + (game_window_rect[2] // 2) - 3,
                             "top":
                                 game_window_rect[1] + (game_window_rect[3] // 2) - 3,
                             "width": 6,
                             "height": 6})
                        FileWriter.write_img(dot_img, rf"{SCREENSHOTS_FOLDER}\{img_time}_61_square.jpg")
                        dot_img = grabber.get_image(
                            {"left": game_window_rect[0] + (game_window_rect[2] // 2) - 10,
                             "top":
                                 game_window_rect[1] + (game_window_rect[3] // 2) - 10,
                             "width": 20,
                             "height": 20})
                        FileWriter.write_img(dot_img, rf"{SCREENSHOTS_FOLDER}\{img_time}_62_full.jpg")
                    if check_dot(hue_point):
                        # click
                        mouse.hold_mouse()
                        sleep(0.001)
                        mouse.release_mouse()
                        sleep(0.001)


                        if _show_cv2:
                            img = grabber.get_image(
                                {"left": int(game_window_rect[0]), "top": int(game_window_rect[1]),
                                 "width": int(game_window_rect[2]),
                                 "height": int(game_window_rect[3])})
                            game_window_rect__center = (game_window_rect[2] // 2, game_window_rect[3] // 2)
                            # print(game_window_rect__center)
                            cv2.circle(img, game_window_rect__center, 5, (255, 255, 0), -1)
                        if _write_cv2:
                            img = grabber.get_image(
                                {"left": int(game_window_rect[0]), "top": int(game_window_rect[1]),
                                 "width": int(game_window_rect[2]),
                                 "height": int(game_window_rect[3])})
                            FileWriter.write_img(img, rf"{SCREENSHOTS_FOLDER}\{img_time}_7_shoot.jpg")
                        print("shoot")
                        _last_shoot = time.perf_counter()
                    else:

                        if _show_cv2:
                            img = grabber.get_image(
                                {"left": int(game_window_rect[0]), "top": int(game_window_rect[1]),
                                 "width": int(game_window_rect[2]),
                                 "height": int(game_window_rect[3])})
                            game_window_rect__center = (game_window_rect[2] // 2, game_window_rect[3] // 2)
                            # print(game_window_rect__center)
                            cv2.circle(img, game_window_rect__center, 5, (255, 255, 0), -1)
                        if _write_cv2:
                            img = grabber.get_image(
                                {"left": int(game_window_rect[0]), "top": int(game_window_rect[1]),
                                 "width": int(game_window_rect[2]),
                                 "height": int(game_window_rect[3])})
                            FileWriter.write_img(img, rf"{SCREENSHOTS_FOLDER}\{img_time}_8_mistake.jpg")
                        print("mistake")
                        mistake_movies = mistake_movies + 1
                else:
                    # Aim only once if shoot is disabled
                    _aim = False

            # Auto deactivate aiming and/or shooting after N seconds
            if AUTO_DEACTIVATE_AFTER is not None:
                if _activation_time + AUTO_DEACTIVATE_AFTER < time.perf_counter():
                    _aim = False



        # if _show_cv2:
        #     img = cv2.putText(img, f"{fps():.2f} | targets = {targets_count}", (20, 120), font,
        #                       1.7, (0, 255, 0), 7, cv2.LINE_AA)
        #     img = cv2.resize(img, (1280, 720))
        #     # cv2.imshow("test", cv2.cvtColor(img, cv2.COLOR_RGB2BGRA))
        #     # mask = cv2.resize(mask, (1280, 720))
        #     cv2.imshow("test", img)
        #     # show img 1 ms
        #     cv2.waitKey(1)
        if _show_fps:
            print(f"FPS: {fps():.2f} | mistakes movies: {mistake_movies}")


def move_left():
    mouse = MouseControls()
    print("rotate left")
    # mouse.move_relative(-int(51.955*26.2534888*2*3), int(rel_diff[1]))
    mouse.move_relative(-int(8182), int(0))


def move_right():
    mouse = MouseControls()
    print("rotate right")
    # mouse.move_relative(int(51.955*26.2534888*2*3), int(rel_diff[1]))
    mouse.move_relative(int(8182), int(0))


def move_up():
    mouse = MouseControls()
    print("rotate up 1/2 fov_v")
    fov = [106.26, 73.74]  # horizontal, vertical
    mouse.move_relative(int(0), -int((8182 * 2 / 360) * fov[1] / 2))


def move_down():
    mouse = MouseControls()
    print("rotate down 1/2 fov_v")
    fov = [106.26, 73.74]  # horizontal, vertical
    mouse.move_relative(int(0), int((8182 * 2 / 360) * fov[1] / 2))


def switch_shoot_state(triggered, hotkey):
    print("switch")
    global _aim, _ret, _activation_time
    _aim = not _aim  # inverse value

    if not _aim:
        _ret = None
    else:
        # run timer
        _activation_time = time.perf_counter()


def exit_app():
    sys.exit(0)


keyboard.add_hotkey(ACTIVATION_HOTKEY, switch_shoot_state, args=('triggered', 'hotkey'))
keyboard.add_hotkey(MOVELEFT_HOTKEY, move_left)
keyboard.add_hotkey(MOVERIGHT_HOTKEY, move_right)
keyboard.add_hotkey(MOVEUP_HOTKEY, move_up)
keyboard.add_hotkey(MOVEDOWN_HOTKEY, move_down)
keyboard.add_hotkey(EXIT_HOTKEY, exit_app, args=[])
if __name__ == "__main__":
    cv2_process()

