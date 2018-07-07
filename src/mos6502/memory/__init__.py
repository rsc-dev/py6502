#!/usr/bin/env python

__author__      = 'Radoslaw Matusiak'
__copyright__   = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__     = 'MIT'


class Memory:
    """Class represents MOS 6502 memory."""

    SIZE = 0x1900  # Default memory size is 64 KB
    PAGE = 0xff  # Page size. Default = 256 B

    def __init__(self, size=SIZE):
        """Initializes memory instance."""
        self._size = size
        self._memory = [0x00] * self._size

    def read_word(self, address):
        assert address < self._size, 'Address out of space!'
        return self._memory[address]

    def write_word(self, address, value):
        assert address < self._size, 'Address out of space!'
        self._memory[address] = value & 0xff

    def load(self, address, data):
        assert address + len(data) < self._size, 'Too much data to write'
        for i in xrange(len(data)):
            self._memory[address + i] = data[i]
            

if __name__ == '__main__':
    pass
