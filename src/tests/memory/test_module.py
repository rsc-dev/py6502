#!/usr/bin/env python

__author__ = 'Radoslaw Matusiak'
__copyright__ = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__ = 'MIT'


import unittest
import random

from mos6502.memory import Memory


class TestMemory(unittest.TestCase):

    def setUp(self):
        self.memory = Memory()

    def test_default_mem(self):
        assert self.memory._size == 0x10000, 'Invalid default memory size!'
        assert len(self.memory._memory) == self.memory._size, 'Invalid initial memory size!'

    def test_simple_write(self):
        for i in range(self.memory.SIZE):
            self.memory.write_byte(i, 0xfa)

        assert self.memory._memory == [0xfa] * self.memory.SIZE, 'Memory write failed!'

    def test_simple_read(self):
        random.seed(0xdeadbeef)

        for i in range(self.memory.SIZE):
            val = random.randint(0, 255)
            self.memory.write_byte(i, val)

            assert self.memory.read_byte(i) == val, 'Invalid memory read value!'

    def test_out_of_range_assert(self):
        try:
            self.memory.read_byte(self.memory.SIZE)
            assert False, 'Out of range assertion not thrown!'
        except AssertionError:
            assert True

    def test_load(self):
        data = [0xde, 0xad, 0xbe, 0xef]

        for i in range(self.memory.SIZE - len(data) - 1):
            self.memory.load(i, data)
            assert self.memory.read_byte(i + 0) == data[0], 'Invalid memory data!'
            assert self.memory.read_byte(i + 1) == data[1], 'Invalid memory data!'
            assert self.memory.read_byte(i + 2) == data[2], 'Invalid memory data!'
            assert self.memory.read_byte(i + 3) == data[3], 'Invalid memory data!'

    def test_load_out_of_range_assert(self):
        data = [0xde, 0xad, 0xbe, 0xef]
        try:
            self.memory.load(self.memory.SIZE - len(data), data)
            assert False, 'Out of range assertion not thrown!'
        except AssertionError:
            assert True


if __name__ == '__main__':
    unittest.main()
