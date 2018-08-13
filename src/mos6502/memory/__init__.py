#!/usr/bin/env python

"""6502 memory implementation."""

__author__ = 'Radoslaw Matusiak'
__copyright__ = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__ = 'MIT'


class Memory(object):
    """Class represents MOS 6502 memory."""

    SIZE = 0x1900  # Default memory size is 64 KB
    PAGE = 0xff  # Page size. Default = 256 B

    def __init__(self, size=SIZE):
        """Initializes memory instance."""
        self._size = size
        self._memory = [0x00] * self._size

    def __getitem__(self, address):
        """
        Getter. Returns byte for given address.

        :param address: Memory address.
        :return: Byte value from given address.
        """
        return self.read_byte(address)

    def read_byte(self, address):
        """
        Read byte from given memory address.

        :param address: Memory address.
        :return: Byte value from given memory address.
        """
        assert address < self._size, 'Address out of space!'
        return self._memory[address]

    def write_byte(self, address, value):
        """
        Write byte to given memory address.

        :param address: Memory address.
        :param value: Byte value to write.
        :return: Nothing.
        """
        assert address < self._size, 'Address out of space!'
        self._memory[address] = value & 0xff

    def read_word(self, address):
        """
        Read word from given memory address.

        :param address: Memory address.
        :return: Word value from given memory address.
        """
        assert address < self._size, 'Address out of space!'

        val = self._memory[address] + self._memory[address + 1] << 8
        return val

    def write_word(self, address, value):
        """
        Write word to given memory address.

        :param address: Memory address.
        :param value: Word value to write.
        :return: Nothing.
        """
        assert address < self._size, 'Address out of space!'

        low = value & 0xff
        high = (value >> 8) & 0xff

        self._memory[address] = low
        self._memory[address + 1] = high

    def load(self, address, data):
        """
        Load given data array to memory starting from given address.

        :param address: Memory address.
        :param data: Array of bytes to write.
        :return: Nothing.
        """
        assert address + len(data) < self._size, 'Too much data to write'
        for i, val in enumerate(data):
            self._memory[address + i] = val


if __name__ == '__main__':
    pass
