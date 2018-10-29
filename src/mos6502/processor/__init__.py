#!/usr/bin/env python

"""MOS6502 MCU."""

__author__ = 'Radoslaw Matusiak'
__copyright__ = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__ = 'MIT'


from mos6502.helpers import to_signed_byte, to_unsigned_byte  # pylint: disable=import-error


class MCU(object):  # pylint: disable=too-few-public-methods
    """6502 processor."""

    def __init__(self):
        # pylint: disable=C0103
        self.a = A()
        self.x = X()
        self.y = Y()

        self.sp = SP()
        self.sp.value = 0xff
        self.sp_base = 1 << 8

        self.pc = PC()
        self.sr = SR()
        # pylint: enable=C0103


class _Register(object):
    """Base class for all registers."""

    def __init__(self, size):

        if size not in [1, 2]:
            raise ValueError('Register size out of range.')

        self._mask = (2 ** (8 * size)) - 1
        self._value = 0x00

    def _value_get(self):
        """
        Register value getter.

        :return: Register value.
        """
        return self._value

    def _value_set(self, val):
        """
        Register value setter.

        :param val: Value to set.
        :return: Nothing.
        """
        self.value_set(val)

    def value_set(self, val):
        """
        Register value setter.

        :param val: Value to set.
        :return: Nothing.
        """
        val = val if val > 0 else to_unsigned_byte(val)
        self._value = val & self._mask

    value = property(_value_get, _value_set)

    @property
    def signed(self):
        """
        Register value getter.

        :return: Signed value.
        """
        return to_signed_byte(self._value)


class A(_Register):  # pylint: disable=invalid-name
    """8 bit Accumulator register."""

    def __init__(self):
        _Register.__init__(self, 1)


class X(_Register):  # pylint: disable=invalid-name
    """8 bit X register."""

    def __init__(self):
        _Register.__init__(self, 1)


class Y(_Register):  # pylint: disable=invalid-name
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


# pylint: disable=C0103
class SR(_Register):
    """8 bit Status Register."""

    def __init__(self):
        _Register.__init__(self, 1)
        self._set_bit_value(5, 1)

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
        assert 0 <= bit <= 7, 'Bit number out of range'
        mask = 1 << bit

        return (self.value & mask) >> bit

    @_Register.value.setter
    def value(self, val):
        """Overriden value setter to make sure unused bit is set."""
        val |= 1 << 5
        super().value_set(val)

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

    # pylint: enable=C0103


if __name__ == '__main__':
    pass
