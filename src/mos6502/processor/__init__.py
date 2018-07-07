#!/usr/bin/env python

__author__      = 'Radoslaw Matusiak'
__copyright__   = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__     = 'MIT'


class Processor:
    """6502 processor."""

    def __init__(self, pc):
        self.a = A(0x00)
        self.x = X(0x00)
        self.y = Y(0x00)
        self.sp = SP(0x00)
        self.pc = PC(pc)
        self.sr = SR(0x00)


class _Register(object):
    """Base class for all registers."""

    def __init__(self, size):

        if size not in [1, 2]:
            raise ValueError('Register size out of range.')

        self._mask = (2 ** (8 * size)) - 1
        self._value = 0x00

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val & self._mask


class A(_Register):
    """8 bit Accumulator register."""

    def __init__(self):
        _Register.__init__(self, 1)


class X(_Register):
    """8 bit X register."""

    def __init__(self):
        _Register.__init__(self, 1)


class Y(_Register):
    """8 bit Y register."""

    def __init__(self):
        _Register.__init__(self, 1)


class SP(_Register):
    """8 bit Stack Pointer register."""

    def __init__(self):
        _Register.__init__(self, 2)


class PC(_Register):
    """8 bit Program Counter register."""

    def __init__(self):
        _Register.__init__(self, 2)


class SR(_Register):
    """8 bit Status Register."""

    def __init__(self):
        _Register.__init__(self, 1)

    def _set_bit_value(self, bit, val):
        """Helper method for setting given bit to 0 or 1 value."""
        assert 0 <= bit < 8, 'Bit number out of range'
        assert val in [0, 1], 'Bit value out of range'

        mask = 1 << bit

        if val == 1:
            self.value = self.value | mask
        else:
            self.value = self.value & (~mask)

    def _get_bit_value(self, bit):
        """Helper bit getter."""
        assert 0 < bit < 8, 'Bit number out of range'
        mask = 1 << bit

        return (self.value & mask) >> bit

    @property
    def N(self):
        """Negative flag getter."""
        return self._get_bit_value(7)

    @N.setter
    def N(self, val):
        """Negative flag setter."""
        self._set_bit_value(7, val)

    @property
    def V(self):
        """Overflow flag getter."""
        return self._get_bit_value(6)

    @V.setter
    def V(self, val):
        """Overflow flag setter."""
        self._set_bit_value(6, val)

    @property
    def B(self):
        """Break flag getter."""
        return self._get_bit_value(4)

    @B.setter
    def B(self, val):
        """Break flag setter."""
        self._set_bit_value(4, val)

    @property
    def D(self):
        """Decimal flag getter."""
        return self._get_bit_value(3)

    @D.setter
    def D(self, val):
        """Decimal flag setter."""
        self._set_bit_value(3, val)

    @property
    def I(self):
        """Interrupt flag getter."""
        return self._get_bit_value(2)

    @I.setter
    def I(self, val):
        """Interrupt flag setter."""
        self._set_bit_value(2, val)

    @property
    def Z(self):
        """Zero flag getter."""
        return self._get_bit_value(1)

    @Z.setter
    def Z(self, val):
        """Zero flag setter."""
        self._set_bit_value(1, val)

    @property
    def C(self):
        """Carry flag getter."""
        return self._get_bit_value(0)

    @C.setter
    def C(self, val):
        """Carry flag setter."""
        self._set_bit_value(0, val)


if __name__ == '__main__':
    pass
