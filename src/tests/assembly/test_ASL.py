#!/usr/bin/env python

__author__ = 'Radoslaw Matusiak'
__copyright__ = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__ = 'MIT'


import unittest

import mos6502.assembly as asm
from mos6502.memory import Memory
from mos6502.processor import MCU


class TestASL(unittest.TestCase):

    def setUp(self):
        self.mcu = MCU()
        self.memory = Memory()


    def test_accumulator(self):
        self.mcu.a.value = 0x64

        asm.ASL.execute(0x0a, [0xf0], self.mcu, self.memory)

        assert self.mcu.a.value == 0x90

    def test_zeropage(self):
        self.mcu.a.value = 0x9a

        self.memory.write_byte(address=0xab, value=0xf0)
        asm.ASL.execute(0x06, [0xab], self.mcu, self.memory)

        assert self.mcu.a.value == 0x90

    def test_zeropage_x_indexed(self):
        self.mcu.a.value = 0x9a
        self.mcu.x.value = 0x22

        self.memory.write_byte(address=0xab, value=0xf0)
        asm.ASL.execute(0x16, [0x89], self.mcu, self.memory)

        assert self.mcu.a.value == 0x90

    def test_absolute(self):
        self.mcu.a.value = 0x9a

        self.memory.write_byte(address=0xf01, value=0xf0)
        asm.ASL.execute(0x0e, [0x01, 0x0f], self.mcu, self.memory)

        assert self.mcu.a.value == 0x90

    def test_absolute_x_indexed(self):
        self.mcu.a.value = 0x9a
        self.mcu.x.value = 0x01

        self.memory.write_byte(address=0xf01, value=0xf0)
        asm.ASL.execute(0x1e, [0x00, 0x0f], self.mcu, self.memory)

        assert self.mcu.a.value == 0x90


if __name__ == '__main__':
    pass