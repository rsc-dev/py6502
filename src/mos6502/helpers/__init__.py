#!/usr/bin/env python

"""Helper methods."""

__author__ = 'Radoslaw Matusiak'
__copyright__ = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__ = 'MIT'


def to_signed_byte(num):
    """
    Convert given byte number to signed byte number.

    :param num: Unsigned byte number in range from 0 to 255.
    :return: Signed number in range from -128 to 127.
    """
    assert 0 <= num <= 255, 'Value out of range (0 - 255)!'

    if num <= 127:
        ret = num
    else:
        ret = (256 - num) * -1

    return ret


def to_unsigned_byte(num):
    """
    Convert given signed byte number to byte number.

    :param num: Signed number in range from -128 to 127.
    :return: Unsigned byte number in range from 0 to 255.
    """
    assert -128 <= num <= 127, 'Value out of range (-128 - 127)!'

    ret = num if num >= 0 else (256 + num)

    return ret


if __name__ == '__main__':
    pass
