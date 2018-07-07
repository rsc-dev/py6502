#!/usr/bin/env python

__author__      = 'Radoslaw Matusiak'
__copyright__   = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__     = 'MIT'


import unittest

from mos6502.processor import A, X, Y, PC, SP, SR


class TestRegs(unittest.TestCase):

    def setUp(self):
        self.a = A()
        self.x = X()
        self.y = Y()
        self.pc = PC()
        self.sp = SP()
        self.sr = SR()

        self.regs_8_b = [self.a, self.x, self.y, self.sp, self.sr]

    def test_init_value(self):
        for reg in self.regs_8_b:
            assert reg.value == 0, 'Invalid initial registry value!'

        assert self.pc.value == 0, 'Invalid initial registry value!'

    def test_pc_valid_values(self):
        for i in xrange(0, 0xffff):
            self.pc.value = i
            assert self.pc.value == i, 'Invalid PC registry value!'

    def test_pc_invalid_values(self):
        try:
            self.pc.value = 0x010000
        except AssertionError:
            assert True

    def test_8_b_regs_valid_values(self):
        for r in self.regs_8_b:
            for i in xrange(0, 0xff):
                r.value = i
                assert r.value == i, 'Invalid registry value!'

    def test_8_b_regs_invalid_values(self):
        try:
            for r in self.regs_8_b:
                r.value = 0x100
        except AssertionError:
            assert True


class TestSR(unittest.TestCase):

    def setUp(self):
        self.sr = SR()

    def test_initial_flags(self):
        assert self.sr.N == 0, 'Invalid SR.N flag value!'

    def test_flags(self):
        self.sr.N = 1

        assert self.sr.value == 1 << 7, 'Invalid SR.N flag value!'
        self.sr.N = 0

        self.sr.V = 1
        assert self.sr.value == 1 << 6, 'Invalid SR.V flag value!'
        self.sr.V = 0

        self.sr.B = 1
        assert self.sr.value == 1 << 4, 'Invalid SR.B flag value!'
        self.sr.B = 0

        self.sr.D = 1
        assert self.sr.value == 1 << 3, 'Invalid SR.D flag value!'
        self.sr.D = 0

        self.sr.I = 1
        assert self.sr.value == 1 << 2, 'Invalid SR.I flag value!'
        self.sr.I = 0

        self.sr.Z = 1
        assert self.sr.value == 1 << 1, 'Invalid SR.Z flag value!'
        self.sr.Z = 0

        self.sr.C = 1
        assert self.sr.value == 1, 'Invalid SR.C flag value!'
        self.sr.C = 0

    def test_invalid_flag_value(self):
        try:
            self.sr.N = 2
        except AssertionError:
            assert True


if __name__ == '__main__':
    unittest.main()
