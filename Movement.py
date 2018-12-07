# encoding: utf-8

import win32api
import win32con

from time import sleep

"""Functions to handle mouse and keyboard movements using win32api
"""


def leftClick(delay=.05):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    sleep(delay)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def leftDown(delay=.05):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    sleep(delay)


def leftUp(delay=.05):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    sleep(delay)


def mousePos(coord):
    win32api.SetCursorPos((coord[0], coord[1]))


# ** Info **

# optionally recieves a box for giving relative position
def getMouse(box=None):
    x, y = win32api.GetCursorPos()
