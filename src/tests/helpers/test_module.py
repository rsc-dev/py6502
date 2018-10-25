#!/usr/bin/env python

__author__ = 'Radoslaw Matusiak'
__copyright__ = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__ = 'MIT'


import unittest

from mos6502.helpers import to_unsigned_byte, to_signed_byte


class TestHelpers(unittest.TestCase):

    def test_to_unsigned_byte_valid_values(self):
        assert to_unsigned_byte(0) == 0x00
        assert to_unsigned_byte(127) == 0x7f
        assert to_unsigned_byte(-128) == 0x80
        assert to_unsigned_byte(-1) == 0xff

    def test_to_unsigned_byte_invalid_values(self):
        try:
            to_unsigned_byte(128)
        except AssertionError:
            assert True

        try:
            to_unsigned_byte(-129)
        except AssertionError:
            assert True

    def test_to_signed_byte_valid_values(self):
        assert to_signed_byte(0x00) == 0
        assert to_signed_byte(0x7f) == 127
        assert to_signed_byte(0x80) == -128
        assert to_signed_byte(0xff) == -1

    def test_to_signed_byte_invalid_values(self):
        try:
            to_unsigned_byte(-1)
        except AssertionError:
            assert True

        try:
            to_unsigned_byte(256)
        except AssertionError:
            assert True


if __name__ == '__main__':
    pass
