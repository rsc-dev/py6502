#!/usr/bin/env python

__author__ = 'Radoslaw Matusiak'
__copyright__ = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__ = 'MIT'


import unittest

import mos6502.assembly as asm
from mos6502.memory import Memory
from mos6502.processor import MCU


class TestADC(unittest.TestCase):

    def setUp(self):
        self.mcu = MCU()
        self.memory = Memory()

    def test_immediate(self):
        self.mcu.a.value = 0x10
        self.mcu.sr.C = 1

        asm.ADC.execute(0x69, [0x0a], self.mcu, self.memory)

        assert self.mcu.a.value == 0x1b

    def test_zeropage(self):
        self.mcu.a.value = 0x10

        self.memory.write_word(address=0xab, value=0x0a)
        asm.ADC.execute(0x65, [0xab], self.mcu, self.memory)

        assert self.mcu.a.value == 0x1a

    def test_zeropage_x_indexed(self):
        self.mcu.a.value = 0x10
        self.mcu.x.value = 0x22

        self.memory.write_word(address=0xab, value=0x0a)
        asm.ADC.execute(0x75, [0x89], self.mcu, self.memory)

        assert self.mcu.a.value == 0x1a

    def test_absolute(self):
        self.mcu.a.value = 0x10

        self.memory.write_word(address=0xf01, value=0x0a)
        asm.ADC.execute(0x6d, [0x01, 0x0f], self.mcu, self.memory)

        assert self.mcu.a.value == 0x1a

    def test_absolute_x_indexed(self):
        self.mcu.a.value = 0x10
        self.mcu.x.value = 0x01

        self.memory.write_word(address=0xf01, value=0x0a)
        asm.ADC.execute(0x7d, [0x00, 0x0f], self.mcu, self.memory)

        assert self.mcu.a.value == 0x1a

    def test_absolute_y_indexed(self):
        self.mcu.a.value = 0x10
        self.mcu.y.value = 0x01

        self.memory.write_word(address=0xf01, value=0x0a)
        asm.ADC.execute(0x79, [0x00, 0x0f], self.mcu, self.memory)

        assert self.mcu.a.value == 0x1a

    def test_indirect_x(self):
        self.mcu.a.value = 0x10
        self.mcu.x.value = 0xaa

        self.memory.write_word(address=0xab, value=0x0a)
        asm.ADC.execute(0x61, [0x01], self.mcu, self.memory)

        assert self.mcu.a.value == 0x1a

    def test_indirect_y(self):
        self.mcu.a.value = 0x10
        self.mcu.y.value = 0xaa

        self.memory.write_word(address=0xab, value=0x0a)
        asm.ADC.execute(0x71, [0x01], self.mcu, self.memory)

        assert self.mcu.a.value == 0x1a


if __name__ == '__main__':
    pass
