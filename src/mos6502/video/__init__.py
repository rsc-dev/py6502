#!/usr/bin/env python

"""Simple Video output."""

__author__ = 'Radoslaw Matusiak'
__copyright__ = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__ = 'MIT'

import pygame
from pygame.locals import *


class VideoScreen(object):

    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode((200, 200))
        pygame.display.set_caption('Video Output')

        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((0, 0, 0))


if __name__ == '__main__':
    v = VideoScreen()
