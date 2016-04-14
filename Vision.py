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
def getBmp(handle=None, dcTuple=None, box=None):

    if handle is None:
        handle = getHandle()
    if dcTuple is None:
        localDC = True
        dcTuple = getDc(handle)
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


def getBox(handle=None, name=None, relative=False):
    if not handle:
        handle = getHandle(name)
    wgui.SetForegroundWindow(handle)
    if relative:
        return wgui.GetClientRect(handle)
    else:
        return wgui.GetWindowRect(handle)


def getCv(bmp=False, color=False, box=None, name=None):
    if bmp is False:
        if box:
            bmp = getBmp(None, None, box)
        elif name:
            bmp = getBmp(None, None, None, name)
        else:
            bmp = getBmp()

    width, height = bmp.GetInfo()['bmWidth'], bmp.GetInfo()['bmHeight']
    size = width, height
    str = bmpString(bmp)
    im = frombuffer('RGB', size, str, 'raw', 'BGRX', 0, 1)
    img = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
    if color is False:
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    return img


def dropDc(handle, dcTuple):
    dcTuple[2].DeleteDC()
    dcTuple[1].DeleteDC()
    wgui.ReleaseDC(handle, dcTuple[0])
    return True


def show(img):
    cv.imshow("Bot img", img)
    cv.waitKey(3000)
    cv.destroyAllWindows()
    return True


def match(img, template):
    w, h = template.shape[::-1]
    res = cv.matchTemplate(img, template, cv.TM_CCOEFF_NORMED)

    _, _, _, res = cv.minMaxLoc(res)
    box = (res[0], res[1], res[0] + w, res[1] + h)
    point = (box[0] + (w / 2), box[1] + (h / 2))
    return point, box


def matchAll(img, template, threshold=0.8):
    w, h = template.shape[::-1]
    res = cv.matchTemplate(img, template, cv.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    res = []
    for pt in zip(*loc[::-1]):
        res.append(pt)
    return res


def draw(img, box):
    if len(box) == 2:  # point
        box = box[0], box[1], box[0] + 2, box[1] + 2
    cv.rectangle(img, (box[0], box[1]), (box[2], box[3]), 255, 4)
    return img


def threshold(img, block=11, C=2):
    blur = cv.medianBlur(img, 5)
    # blur = cv.GaussianBlur(img, (3, 3), 0)
    gauss = cv.ADAPTIVE_THRESH_GAUSSIAN_C
    thresh = cv.THRESH_BINARY
    result = cv.adaptiveThreshold(blur, 255, gauss, thresh, block, C)

    return result


def reduce(img):

    # __Slow as fuck:__
    # from scipy.cluster.vq import kmeans, vq
    # pixel = np.reshape(img, (img.shape[0] * img.shape[1], 3))
    # centroids, _ = kmeans(pixel, 6)  # six colors will be found
    # qnt, _ = vq(pixel, centroids)
    # centersIdx = np.reshape(qnt, (img.shape[0], img.shape[1]))
    # clustered = centroids[centersIdx]
    # img = np.flipud(clustered)
    #     Z = img.reshape((-1, 3))
    # Z = np.float32(Z)
    # C = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    # K = 2
    # ret, lbl, cent = cv.kmeans(Z, K, None, C, 10, cv.KMEANS_RANDOM_CENTERS)
    # cent = np.uint8(cent)
    # res = cent[lbl.flatten()]
    # res2 = res.reshape((img.shape))

    return True


# Misc functions
def bmpString(bmp):
    return bmp.GetBitmapBits(True)


def bmpTuple(bmp):
    return bmp.GetBitmapBits(False)


def getRgb(long):  # gets the rgb code from a long formatted number
    r, g, b = long & 255, (long >> 8) & 255, (long >> 16) & 255
    return int(r), int(g), int(b)


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
                    imgs = getCv(getBmp(handle), True)
                    showImg(imgs)
                except Exception, e:
                    print e
    try:
        wgui.EnumChildWindows(handle, childHandler, None)
    except Exception, e:
        print e
    return True


if __name__ == '__main__':

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
