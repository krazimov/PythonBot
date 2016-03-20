# import os
# import win32api
import win32con
import win32ui
import win32gui as wgui

from time import sleep, time
# from collections import deque
import numpy as np
import Image
import cv2 as cv

import Sea

# Globals
# ------------------

windowName = "Nox"
ColorReduct = 32


def getHandle(name=None):
    if name is None:
        return wgui.GetDesktopWindow()  # current window
    return wgui.FindWindow(None, name)


# gets a Device Context from given handle, window name xor default window
def getDc(handle=None, windowName=None):
    if handle is None:
        handle = getHandle(windowName)

    winContext = wgui.GetDC(handle)
    devContext = win32ui.CreateDCFromHandle(winContext)
    comContext = devContext.CreateCompatibleDC()

    # Remember to release Dc afterwards!
    return winContext, devContext, comContext


# gets bmp image from device context or handle
def getBmp(handle=None, dcTuple=None, Box=None):

    if handle is None:
        handle = getHandle()
    if dcTuple is None:
        localDC = True
        dcTuple = getDc(handle)

    left, up, right, down = wgui.GetWindowRect(handle) if Box is None else Box

    height, width = down - up, right - left
    size = width, height

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(dcTuple[1], width, height)
    dcTuple[2].SelectObject(bmp)
    dcTuple[2].BitBlt((0, 0), size, dcTuple[1], (0, 0), win32con.SRCCOPY)

    if localDC:
        dropDc(handle, dcTuple)

    return bmp


# saves a bmp file from a dc
def saveBmp(handle=None, fileName="{}.bmp".format(time())):
    if handle is None:
        handle = getHandle()
    dcTuple = getDc(handle)
    bmp = getBmp(handle)

    bmp.SaveBitmapFile(dcTuple[2], fileName)
    dropDc(handle, dcTuple)
    return fileName


# gets rgb codes of the pixel given
def getPixel(x, y, handle=None):
    if handle is None:
        handle = getHandle()
    winDC = wgui.GetDC(handle)

    color = wgui.GetPixel(winDC, x, y)
    wgui.ReleaseDC(handle, winDC)

    rgb = getRgb(color)
    return rgb


def getRgb(long):  # gets the rgb code from a long formatted number
    r, g, b = long & 255, (long >> 8) & 255, (long >> 16) & 255
    return int(r), int(g), int(b)


def getCv(bmp=False, color=False):
    if bmp is False:
        bmp = getBmp()
    height = bmp.GetInfo()['bmHeight']
    width = bmp.GetInfo()['bmWidth']
    size = bmp.GetInfo()['bmWidth'], bmp.GetInfo()['bmHeight']
    str = bmpString(bmp)
    im = Image.frombuffer('RGB', size, str, 'raw', 'BGRX', 0, 1)
    img = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
    if color is False:
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    return img


def match(img, goal):
    goal = cv.cvtColor(goal, cv.COLOR_BGR2GRAY)
    w, h = goal.shape[::-1]

    img = threshold(img)
    goal = threshold(goal)

    # img = cv.Laplacian(img, cv.CV_32F)
    # goal = cv.Laplacian(goal, cv.CV_32F)

    # All methods for comparison
    meth = cv.TM_CCOEFF_NORMED  # cv.TM_CCOEFF
    # meth = cv.TM_CCORR_NORMED  # cv.TM_CCORR
    # meth = cv.TM_SQDIFF #  cv.TM_SQDIFF_NORMED  # Use minLoc

    res = cv.matchTemplate(img, goal, meth)
    minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(res)

    cv.rectangle(img, maxLoc, (maxLoc[0] + w, maxLoc[1] + h), 200, 2)

    # print maxVal
    # print maxLoc

    showImg(img)
    return res


def showImg(img):
    cv.imshow("Bot img", img)
    cv.waitKey(3000)
    cv.destroyAllWindows()
    return True


def downsample(img):
    cv.pyrDown(img, sample, (500, 500))
    showImg(img)
    pass


def threshold(img, block=3, C=3):
    # blur = cv.medianBlur(img, 5)
    blur = cv.GaussianBlur(img, (3, 3), 0)
    gauss = cv.ADAPTIVE_THRESH_GAUSSIAN_C
    thresh = cv.THRESH_BINARY
    result = cv.adaptiveThreshold(blur, 255, gauss, thresh, block, C)

    return result


def bmpString(bmp):
    return bmp.GetBitmapBits(True)


def bmpTuple(bmp):
    return bmp.GetBitmapBits(False)


def dropDc(handle, dcTuple):
    dcTuple[2].DeleteDC()
    dcTuple[1].DeleteDC()
    wgui.ReleaseDC(handle, dcTuple[0])
    return True


def winList():
    def winEnumHandler(handle, ctx):
        if wgui.IsWindowVisible(handle):
            print handle, wgui.GetWindowText(handle)
            saveBmp(handle)
    # win32gui.EnumChildWindows(hwnd, callback, None)
    wgui.EnumWindows(winEnumHandler, None)
    return True


if __name__ == '__main__':
    Sea.getBox()

    '''

    # wgui.UpdateWindow(handle)
    # wgui.SetForegroundWindow(handle)
    # wgui.SetFocus(handle)
    # handle = wgui.WindowFromPoint((x, y))
    # name = win32api.GetActiveWindow()
    # pos = wgui.ScreenToClient(handle, (x, y))
    # pos = wgui.ClientToScreen(handle, (x, y))
    # pos = wgui.GetWindowPlacement(handle)

    # OpenCV
    cv.setUseOptimized(True)
    cv.rectangle(img, (384, 0), (510, 128), (0, 255, 0), 3)
    ball = img[280:340, 330:390]
    laplacian = cv.Laplacian(img, cv.CV_64F)
    print img.shape

    # find contours
    ret, thrs = cv.threshold(img, 127, 255, 0)
    cont, hier = cv.findContours(thrs, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cnt = cont[4]
    cv.drawContours(img, [cnt], 0, (0, 255, 0), 3)

    # Contour properties
    area = cv.contourArea(cnt)
    x, y, w, h = cv.boundingRect(cnt)
    extent = float(area)/(w*h)

    # extreme points
    leftmost = tuple(cnt[cnt[:, :, 0].argmin()][0])
    rightmost = tuple(cnt[cnt[:, :, 0].argmax()][0])
    topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])
    bottommost = tuple(cnt[cnt[:, :, 1].argmax()][0])

    # bounding rectangle
    x, y, w, h = cv.boundingRect(cnt)
    cv.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # rotated rectangle
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(img, [box], 0, (0, 0, 255), 2)
    '''
