# import os
# import win32api
import win32con
from win32ui import CreateDCFromHandle, CreateBitmap
import win32gui as wgui

from time import sleep, time
from Image import frombuffer
import numpy as np
import cv2 as cv

# Globals
# ------------------

# defaultWin = "Nox App Player"
defaultWin = "Sea.png - Sublime Text (UNREGISTERED)"
cv.setUseOptimized(True)


# Windows API functions
def getHandle(name=None):
    if name is None:
        return wgui.GetDesktopWindow()  # current window
    return wgui.FindWindow(None, name)


# gets a Device Context from given handle, window name xor default window
def getDc(handle=None, name=None):
    if handle is None:
        handle = getHandle(name)

    winContext = wgui.GetDC(handle)
    devContext = CreateDCFromHandle(winContext)
    comContext = devContext.CreateCompatibleDC()

    # Remember to release Dc afterwards!
    return winContext, devContext, comContext


# gets bmp image from device context or handle
def getBmp(box=None, handle=None, dcTuple=None):

    if handle is None:
        handle = getHandle()
    if dcTuple is None:
        localDC = True
        dcTuple = getDc(handle)
    else:
        localDC = False
    left, up, right, down = box if box else wgui.GetWindowRect(handle)
    height, width = down - up, right - left
    size = width, height
    bmp = CreateBitmap()
    bmp.CreateCompatibleBitmap(dcTuple[1], width, height)
    dcTuple[2].SelectObject(bmp)
    dcTuple[2].BitBlt((0, 0), size, dcTuple[1], (left, up), win32con.SRCCOPY)
    if localDC:
        dropDc(handle, dcTuple)
    return bmp


# saves a bmp file from a dc
def saveBmp(handle=None, fileName="{}.bmp".format(time())):
    if handle is None:
        handle = getHandle()
    dcTuple = getDc(handle)
    bmp = getBmp(None, handle)

    bmp.SaveBitmapFile(dcTuple[2], fileName)
    dropDc(handle, dcTuple)
    return fileName


def getBox(handle=None, name=None, relative=False):
    if handle is None:
        handle = getHandle(name)
    if relative:
        box = wgui.GetClientRect(handle)
    else:
        box = wgui.GetWindowRect(handle)
    return box


def getCv(bmp=False, color=0, box=None):
    if bmp is False:
        bmp = getBmp(box) if box else getBmp()

    formats = {0: cv.COLOR_RGB2GRAY, 1: cv.COLOR_RGB2BGR, 2: cv.COLOR_RGB2HSV}
    width, height = bmp.GetInfo()['bmWidth'], bmp.GetInfo()['bmHeight']
    size = width, height
    str = bmpString(bmp)
    im = frombuffer('RGB', size, str, 'raw', 'BGRX', 0, 1)
    img = cv.cvtColor(np.array(im), formats[color])
    return img


def dropDc(handle, dcTuple):
    dcTuple[2].DeleteDC()
    dcTuple[1].DeleteDC()
    wgui.ReleaseDC(handle, dcTuple[0])
    return True


def show(img, title='Bot Img', secs=3):
    cv.imshow(title, img)
    cv.waitKey(secs * 1000)
    cv.destroyAllWindows()
    return True


def match(img, template, threshold=0.7):
    w, h = template.shape[::-1]

    res = cv.matchTemplate(img, template, cv.TM_CCOEFF_NORMED)
    _, maxVal, _, maxLoc = cv.minMaxLoc(res)

    if maxVal >= threshold:
        point = (maxLoc[0] + (w / 2), maxLoc[1] + (h / 2))
        box = (maxLoc[0], maxLoc[1], maxLoc[0] + w, maxLoc[1] + h)
    else:
        point, box = None, None
    return point, box


def matchAll(img, template, threshold=0.7):
    w, h = template.shape[::-1]
    res = cv.matchTemplate(img, template, cv.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    res = []
    for pt in zip(*loc[::-1]):
        if (res[-1][0] - 10 > pt[0] > res[-1][0] + 10):
            print "sdadas"
        res.append((pt[0] + w / 2, pt[1] + h / 2))
    return res


def draw(img, box, width=4):
    if len(box) == 2:  # point
        box = box[0] - 5, box[1] - 5, box[0] + 5, box[1] + 5
    cv.rectangle(img, (box[0], box[1]), (box[2], box[3]), 255, width)
    return img


def threshold(img, block=11, C=2):
    blur = cv.medianBlur(img, 5)
    # blur = cv.GaussianBlur(img, (3, 3), 0)
    gauss = cv.ADAPTIVE_THRESH_GAUSSIAN_C
    thresh = cv.THRESH_BINARY
    result = cv.adaptiveThreshold(blur, 255, gauss, thresh, block, C)

    return result


def maskColor(img, mode=0, color=0):

    # ranges of color in HSV
    # 0 = info, 1 = pure white
    bound = {
        0: (np.array([8, 90, 100]), np.array([56, 255, 255])),
        1: (np.array([0, 0, 254]), np.array([1, 1, 255]))
    }
    if color >= 0:
        space = {0: cv.COLOR_BGR2HSV, 1: cv.COLOR_RGB2HSV}
        # Convert BGR to HSV
        img = cv.cvtColor(img, space[color])

    lower = bound[mode][0]
    upper = bound[mode][1]
    mask = cv.inRange(img, lower, upper)  # Threshold to get color
    # res = cv.bitwise_and(img, img, mask=mask) # mask and original image

    return mask


# Misc functions
def bmpString(bmp):
    return bmp.GetBitmapBits(True)


def bmpTuple(bmp):
    return bmp.GetBitmapBits(False)


def getRgb(rgbInt):  # gets the rgb code from a rgbInt formatted number
    r, g, b = rgbInt & 255, (rgbInt >> 8) & 255, (rgbInt >> 16) & 255
    return int(r), int(g), int(b)


def getRgbInt(rgb):
    red = rgb[0]
    green = rgb[1]
    blue = rgb[2]
    RGBint = (red << 16) + (green << 8) + blue
    return RGBint


def winList(showImg=False):
    print "---------\nWindows list\n---------"

    def winEnumHandler(handle, ctx):
        if wgui.IsWindowVisible(handle):
            print handle, wgui.GetWindowText(handle)
            if showImg:
                try:
                    showImg(getCv(getBmp(handle), True))
                except Exception, e:
                    print e
    wgui.EnumWindows(winEnumHandler, None)
    print "---------"
    return True


def winChilds(handle, img=False):
    def childHandler(handle, ctx):
        if wgui.IsWindowVisible(handle):
            print handle, wgui.GetWindowText(handle)
            if img:
                try:
                    imgs = getCv(getBmp(None, handle), True)
                    showImg(imgs)
                except Exception, e:
                    print e
    try:
        wgui.EnumChildWindows(handle, childHandler, None)
    except Exception, e:
        print e
    return True


if __name__ == '__main__':
    example = cv.imread('Examples/buff.png')
    maskColor(example)
    pass
    '''

    # wgui.BringWindowToTop(handle)
    # wgui.UpdateWindow(handle)
    # wgui.SetForegroundWindow(handle)
    # wgui.SetFocus(handle)
    # handle = wgui.WindowFromPoint((x, y))
    # name = win32api.GetActiveWindow()
    # pos = wgui.ScreenToClient(handle, (x, y))
    # pos = wgui.ClientToScreen(handle, (x, y))
    # pos = wgui.GetWindowPlacement(handle)

    # OpenCV
    cv.rectangle(img, (384, 0), (510, 128), (0, 255, 0), 3)
    ball = img[280:340, 330:390]
    laplacian = cv.Laplacian(img, cv.CV_64F)

    # find contours
    ret, thrs = cv.threshold(img, 127, 255, 0)
    cont, hier = cv.findContours(thrs, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cnt = cont[4]
    cv.drawContours(img, [cnt], 0, (0, 255, 0), 3)

    # Contour properties
    area = cv.contourArea(cnt)
    x, y, w, h = cv.boundingRect(cnt)
    extent = float(area)/(w*h)

    # bounding rectangle
    x, y, w, h = cv.boundingRect(cnt)
    cv.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    '''
