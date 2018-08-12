#!/usr/bin/env python

__author__ = 'Radoslaw Matusiak'
__copyright__ = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__ = 'MIT'


from mos6502.memory import Memory
from mos6502.processor import MCU


class Emulator(object):

    def __init__(self):
        self.memory = Memory()
        self.processor = MCU()

    def load(self, address, data):
        """
        Load data into memory.

        :param address: Memory address where data will be loaded.
        :param data: Data to be loaded.
        :return: Nothing.
        """
        self.memory.load(address, data)

    @staticmethod
    def run():
        """
        Run emulator loop.

        :return: Nothing.
        """

        while True:
            # 1. fetch
            pass


if __name__ == '__main__':
    pass
