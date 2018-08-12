#!/usr/bin/env python

__author__ = 'Radoslaw Matusiak'
__copyright__ = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__ = 'MIT'


import unittest

import mos6502.assembly as asm
from mos6502.assembly import AddressMode
from mos6502.memory import Memory
from mos6502.processor import MCU


class TestAddressMode(unittest.TestCase):

    def setUp(self):
        self.memory = Memory()
        data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f]
        self.memory.load(0x0, data)
        self.memory.load(0x0100, data)

        self.mcu = MCU()

    def test_address_mode_operand(self):
        test_val = 0x33
        self.mcu.a.value = test_val
        operand, address = AddressMode.calculate_operand(AddressMode.ACCUMULATOR, [], self.mcu, self.memory)

        assert operand == test_val, 'Invalid Accumulator operand value!'

    def test_address_mode_absolute(self):
        operand, address = AddressMode.calculate_operand(AddressMode.ABSOLUTE, [0x02, 0x01], self.mcu, self.memory)

        assert operand == 0x03, 'Invalid Absolute operand value!'

    def test_address_mode_absolute_x_indexed(self):
        self.mcu.x.value = 0x03
        operand, address = AddressMode.calculate_operand(AddressMode.ABSOLUTE_X_INDEXED, [0x02, 0x01], self.mcu, self.memory)

        assert operand == 0x06, 'Invalid Absolute X indexed operand value!'

    def test_address_mode_absolute_y_indexed(self):
        self.mcu.y.value = 0x01
        operand, address = AddressMode.calculate_operand(AddressMode.ABSOLUTE_Y_INDEXED, [0x02, 0x01], self.mcu, self.memory)

        assert operand == 0x04, 'Invalid Absolute Y indexed operand value!'

    def test_address_mode_immediate(self):
        operand, address = AddressMode.calculate_operand(AddressMode.IMMEDIATE, [0x77], self.mcu, self.memory)

        assert operand == 0x77, 'Invalid Immediate operand value!'

    def test_address_mode_implied(self):
        operand, address = AddressMode.calculate_operand(AddressMode.IMPLIED, [], self.mcu, self.memory)

        assert operand is None, 'Invalid Implied operand value!'


if __name__ == '__main__':
    pass
