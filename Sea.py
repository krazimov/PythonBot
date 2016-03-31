from time import sleep

import Vision
import Movement


class Ref:
    folder = "Templates/Vikings/Sea/"

    box = folder + "boxSea.png"
    colo = folder + "coloSea.png"
    raid = folder + "attackSea.png"
    dist = folder + "distanceSea.png"
    town = folder + "townNameSea.png"
    ammo = folder + "ammoIcon.png"
    slow = folder + "speed1Icon.png"
    fair = folder + "speed2Icon.png"
    fast = folder + "speed3Icon.png"

    pass


class Coord:
    pass


class Color:
    bar = 255, 255, 255
    pass


def getBox():
    screen = Vision.getCv()
    handle = Vision.getHandle(screen)

    # downsample - threshold
    img = Vision.getBmp(handle)
    Vision.showImg(img)
    # ref = Vision.cv.imread(Ref.ammo, 1)
    # pos = Vision.match(screen, ref)

    # downsample - threshold
    img = Vision.getBmp(screen)
    Vision.showImg(img)
    # find box
    # simplify
    # get edge

    # template

    return False


def getBonus(img):
    position = ""
    return position


def navigate():
    bonus = getBonus()
    while not bonus:  # Waiting for bonuses to appear
        sleep(1)
        print "Waiting bonus bar"
        bonus = getBonus()
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
    pass
