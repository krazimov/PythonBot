# import os
import win32api
import win32con

from time import sleep


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
    win32api.SetCursorPos((xPad + coord[0], yPad + coord[1]))


# ** Info **

# optionally recieves a box for giving relative position
def getMouse(box=None):
    x, y = win32api.GetCursorPos()
    if box is not None:
        x -= box[0]
        y -= box[1]

    print x, y
