from time import sleep

# import Vision
import Vision
import Movement


class Ref:
    folder = "Templates/Vikings/Sea/"

    raid = folder + "attackSea.bmp"
    dist = folder + "distanceSea.bmp"
    town = folder + "townNameSea.bmp"
    ammo = folder + "ammoIcon.bmp"
    slow = folder + "speed1Icon.bmp"
    fair = folder + "speed2Icon.bmp"
    fast = folder + "speed3Icon.bmp"
    push = folder + "row.bmp"

    boostBox = -760, - 60, - 40, + 110


# Constants
winName = "Sea.png - Sublime Text (UNREGISTERED)"


def sail():
    # get row position
    pos = Vision.getBox(None, winName)
    img = Vision.getCv(Vision.getBmp(None, None, pos), True)
    imgbc = Vision.getCv(Vision.getBmp(None, None, pos), False)
    rowBtn = rowPos(imgbc, (pos[0], pos[1]))
    target, box = buffPos(rowBtn, (pos[0], pos[1]))
    print target, box
    img = Vision.draw(img, box)
    Vision.show(img)
    # Find stable bar
    # point = list(point)
    # point[0] = point[0] + Pos.offsetRow

    # get box indicators
    Vision.show(img)

    pass


def buffPos(ref, offset=False):
    box = Ref.boostBox
    box = ref[0] + box[0], ref[1] + box[1], ref[0] + box[2], ref[1] + box[3]
    img = Vision.getCv(Vision.getBmp(None, None, box))
    fast = Vision.cv.imread(Ref.fast, 0)
    point, pos = Vision.match(img, fast)

    if offset:
        px = box[0] - offset[0]
        py = box[1] - offset[1]
        point = point[0] + px, point[1] + py
        pos = pos[0] + px, pos[1] + py, pos[2] + px, pos[3] + py
    return point, pos


def rowPos(img, offset=False):
    push = Vision.cv.imread(Ref.push, 0)
    point, _ = Vision.match(img, push)
    if offset:
        return (point[0] + offset[0], point[1] + offset[1])
    return point


def rowTo():
    pass


def navigate():
    bonus = buffPos()
    while not bonus:  # Waiting for bonuses to appear
        sleep(1)
        print "Waiting bonus bar"
        bonus = buffPos()
    print "bonuses found {}".format(bonus)

    barPos = getBar()
    while not barPos:
        print "activating bar"
        Movement.mousePos((Coord.row))
        Movement.leftDown()
        sleep(.5)  # Waiting for bar to appear
        barPos = getBar()
    print "Bar position registered at {}".format(barPos)

    if "fast" in bonus:
        x = bonus["fast"]

    elif "ammo" in bonus:
        x = bonus["ammo"]

    print "Chosen target {}".format(x)

    while dist != barMatch(x):
        if -2 < dist < 2:
            leftUp()
            sleep(1)  # ui takes a time to clear
            print "action done"

    leftUp()
    return True

if __name__ == '__main__':
    sail()
    pass
