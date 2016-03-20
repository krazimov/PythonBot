import os
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image

from glob import glob
from random import randint
from os.path import join, dirname
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty


class Mood:

    names = ['Ask', 'Focus', 'Fun', 'Joy', 'Sad', 'Shock', 'Sleep', 'Wink']


def moodPath(mood='Sleep', absolute=False):
    path = "\Mood\{}.png".format(mood)
    if absolute:
        path = dirname(__file__) + path
    print path
    return path


class Bot(Widget):
    pass


class Picture(Scatter):
    '''Check the rule <Picture>'''
    source = StringProperty(None)


class BotApp(App):
    def build(self):
        root = self.root

        try:
            path = moodPath('Ask', True)
            picture = Picture(source=path)
            root.add_widget(picture)
        except Exception as e:
            print "Pictures: Unable to load {}".format(path)

        return Bot()

    def on_pause(self):
        return True


BotApp().run()
