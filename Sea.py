import sys
from time import sleep, time

import Vision
import Movement


class Ref:
    winName = "Nox App Player"
    # winName = "buff.png - Sublime Text (UNREGISTERED)"

    folder  = "Templates/Vikings/Sea/"
    dist = folder + "distanceSea.bmp"
    town = folder + "townNameSea.bmp"
    ammo = folder + "ammoIcon.bmp"
    slow = folder + "speed1Icon.bmp"
    fair = folder + "speed2Icon.bmp"
    fast = folder + "speed3Icon.bmp"
    row  = folder + "row.bmp"

    buffBox = -810, - 75, - 55, + 130
    barBox = -750, + 20, - 70, + 24

#  globals
handle = Vision.getHandle()
dcTuple = Vision.getDc()


def sail(winName=None):
    if winName is None:
        winName = Ref.winName
    box = Vision.getBox(None, winName)
    screen = Vision.getCv(Vision.getBmp(box), 1)

    sys.stdout.write('\nSearching Row btn')
    rowBtn = getItem(box, Ref.row)
    buffBox = getRefBox(rowBtn, Ref.buffBox)
    barBox = getRefBox(rowBtn, Ref.barBox)
    for x in xrange(1, 10):
        Movement.leftUp()
        buff = getBuff(offset(buffBox), rowBtn, Ref.fast)
        startRow(rowBtn)
        sleep(.8)
        rowTo(offset(barBox), buff)
        Movement.leftUp()
        sleep(.8)

    Vision.dropDc(handle, dcTuple)
    return True


def getRefBox(ref, box=None, absolute=False):
    if box is None:
        box = Ref.boostBox
    left, up, right, down = box
    area = ref[0] + left, ref[1] + up, ref[0] + right, ref[1] + down
    if absolute:
        area = offset(area, ref)
    return area


def getItem(box, target, absolute=False):
    start = time()
    point = None
    ref = Vision.cv.imread(target, 0)
    while point is None:  # waiting for the interface
        sys.stdout.write('.')
        img = Vision.getCv(Vision.getBmp(box, handle, dcTuple), 2)
        mask = Vision.maskColor(img, 0, -1)
        point, _ = Vision.match(mask, ref)
    if absolute:
        point = offset(point, box)
    print("Item found - %s sec " % (time() - start))
    return point


def getBuff(box, ref, target=None):

    sys.stdout.write('\nSearching buff')
    start = time()

    point = None
    multiple = False
    if target is None:
        targets = (
            Vision.cv.imread(Ref.fast, 0),
            Vision.cv.imread(Ref.ammo, 0),
            Vision.cv.imread(Ref.fair, 0))
        multiple = True
    else:
        refImg = Vision.cv.imread(target, 0)

    while point is None:
        sys.stdout.write('.')
        start = time()
        img = Vision.getCv(Vision.getBmp(box, handle), 2)
        mask = Vision.maskColor(img, 0, -1)
        if multiple:
            for refImg in targets:
                point, _ = Vision.match(mask, refImg)
                if point is not None:
                    pass
        else:
            point, _ = Vision.match(mask, refImg)

    point = offset(point, box)  # Convert back to parent coords
    print("Buff found at {} in {} sec").format(point[0], (time() - start))
    return point


def startRow(coords):
    if coords:
        Movement.leftUp()
        Movement.mousePos(coords)
        Movement.leftDown()
    return coords


def rowTo(box, coords):
    # TODO: Resize
    start  = time()
    sys.stdout.write('\nTracking bar')
    done = False
    x, y = coords[0], box[1] + (box[3] - box[1]) / 2
    area = [x, box[1], box[2], box[3]]
    while done is False:
        sys.stdout.write('.')
        img  = Vision.getCv(Vision.getBmp(area, handle), 2)
        mask = Vision.maskColor(img, 1, -1)
        cnts = Vision.cv.findContours(
            mask.copy(),
            Vision.cv.RETR_EXTERNAL,
            Vision.cv.CHAIN_APPROX_SIMPLE)[-2]

        if len(cnts) > 0:
            c = max(cnts, key=Vision.cv.contourArea)
            (bar, _), _ = Vision.cv.minEnclosingCircle(c)
            area[3] = int(bar) + 5
            if area[3] < 15:
                Movement.leftUp()
                done = True
    print("Row completed in {}\n").format((time() - start))
    return True


def rowToByPixel():
    handle = Vision.getHandle()
    winDC  = Vision.wgui.GetDC(handle)
    done = False
    x, y = coords[0], box[1] + (box[3] - box[1]) / 2
    bar, span  = box[2], bar - 20

    while done is False:
        for px in range(x, bar):
            color = Vision.wgui.GetPixel(winDC, px, y)
            if color == 16777215:
                bar, span  = px, bar - 10
                break
        if (bar - x) < 15:
            Movement.leftUp()
            done = True
    Vision.wgui.ReleaseDC(handle, winDC)
    return True


def offset(coords, pad=None, reverse=False):
    if coords is None:
        return None
    if pad is None:
        pad = Vision.getBox(None, Ref.winName)
    if reverse:
        x, y = -pad[0], -pad[1]
    else:
        x, y = pad[0], pad[1]
    if len(coords) == 2:  # point
        res = coords[0] + x, coords[1] + y
    else:  # Box, I hope
        res = coords[0] + x, coords[1] + y, coords[2] + x, coords[3] + y
    return res


if __name__ == '__main__':
    sail()
    pass
