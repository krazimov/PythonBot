# encoding: utf-8

from time import sleep

import Vision
import Movement


class Ref:
    winName = "Sid Meier's Civilization V (DX11)"
    folder = "Templates/Civ5/"
    coin   = folder + "coin.bmp"
    landBtn   = folder + "landBuyBtn.bmp"


def buyLand():
    box = Vision.getBox(None, Ref.winName)
    img = Vision.getCv(Vision.getBmp(box), False)
    buyMode = getLandBuy(img)
    target = Vision.cv.imread(Ref.coin, 0)
    array = Vision.matchAll(img, target)

    for point in array:
        Movement.mousePos(point)
        Movement.leftClick()
        Movement.mousePos(buyMode)
        Movement.leftClick()
        sleep(.3)


def getLandBuy(img):
    target = Vision.cv.imread(Ref.landBtn, 0)
    point, _ = Vision.match(img, target)
    return (point[0] + 100, point[1])


if __name__ == '__main__':
    buyLand()
    pass
