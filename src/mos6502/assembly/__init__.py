#!/usr/bin/env python
# pylint: disable=too-many-lines

"""6502 assembly."""

__author__ = 'Radoslaw Matusiak'
__copyright__ = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__ = 'MIT'


from enum import Enum

from mos6502.helpers import to_signed_byte  # pylint: disable=import-error


class AddressMode(Enum):
    """Address modes enum."""

    ACCUMULATOR = 1
    ABSOLUTE = 2
    ABSOLUTE_X_INDEXED = 3
    ABSOLUTE_Y_INDEXED = 4
    IMMEDIATE = 5
    IMPLIED = 6
    INDIRECT = 7
    INDEXED_X_INDIRECT = 8
    INDIRECT_Y_INDEXED = 9
    RELATIVE = 10
    ZEROPAGE = 11
    ZEROPAGE_X_INDEXED = 12
    ZEROPAGE_Y_INDEXED = 13

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    @staticmethod
    def calculate_operand(mode, bytez, mcu, memory):
        """
        Calculate instruction operand based on address mode.

        :param mode: Address mode.
        :param bytez: Raw operation bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Calculated operation operand.
        """
        address = None
        operand = None

        if mode == AddressMode.ACCUMULATOR:
            operand = mcu.a.value
        elif mode == AddressMode.ABSOLUTE:
            assert len(bytez) == 2, 'Invalid bytes length for Absolute address mode.'
            address = bytez[1] << 8 | bytez[0]
            operand = memory[address]
        elif mode == AddressMode.ABSOLUTE_X_INDEXED:
            assert len(bytez) == 2, 'Invalid bytes length for Absolute X indexed address mode.'
            address = bytez[1] << 8 | bytez[0]
            address += mcu.x.value
            operand = memory[address]
        elif mode == AddressMode.ABSOLUTE_Y_INDEXED:
            assert len(bytez) == 2, 'Invalid bytes length for Absolute Y indexed address mode.'
            address = bytez[1] << 8 | bytez[0]
            address += mcu.y.value
            operand = memory[address]
        elif mode == AddressMode.IMMEDIATE:
            assert len(bytez) == 1, 'Invalid bytes length for Immediate address mode.'
            operand = bytez[0]
        elif mode == AddressMode.IMPLIED:
            pass  # Operand implied
        elif mode == AddressMode.INDIRECT:
            assert len(bytez) == 2, 'Invalid bytes length for Indirect address mode.'
            address = bytez[1] << 8 | bytez[0]
            operand = address
            low = memory[address]
            high = memory[address+1]
            address = high << 8 | low
        elif mode == AddressMode.INDEXED_X_INDIRECT:
            assert len(bytez) == 1, 'Invalid bytes length for Indexed Indirect address mode.'
            address = (bytez[0] + mcu.x.value) & 0xff
            address = memory[address] + (memory[address + 1] << 8)
            operand = memory[address]
        elif mode == AddressMode.INDIRECT_Y_INDEXED:
            assert len(bytez) == 1, 'Invalid bytes length for Indirect Indexed address mode.'
            address = (bytez[0]) & 0xff
            address = memory[address] + (memory[address + 1] << 8) + mcu.y.value
            operand = memory[address]
        elif mode == AddressMode.RELATIVE:
            assert len(bytez) == 1, 'Invalid bytes length for Relative address mode.'
            address = to_signed_byte(bytez[0]) + mcu.pc.value
            operand = memory[address]
        elif mode == AddressMode.ZEROPAGE:
            assert len(bytez) == 1, 'Invalid bytes length for Zeropage address mode.'
            address = bytez[0]
            operand = memory[address]
        elif mode == AddressMode.ZEROPAGE_X_INDEXED:
            assert len(bytez) == 1, 'Invalid bytes length for Zeropage X indexed address mode.'
            address = (bytez[0] + mcu.x.value) & 0xff
            operand = memory[address]
        elif mode == AddressMode.ZEROPAGE_Y_INDEXED:
            assert len(bytez) == 1, 'Invalid bytes length for Zeropage Y indexed address mode.'
            address = (bytez[0] + mcu.y.value) & 0xff
            operand = memory[address]
        else:
            assert False, 'Invalid mode!'

        return operand, address


class Instruction(object):  # pylint: disable=too-few-public-methods
    """Base class for assembly instructions."""

    @classmethod
    def disassm(cls, opcode, mcu, memory, bytez):
        ret = ''

        address_mode, _, _, _ = cls.INSTRUCTIONS[opcode]

        if address_mode == AddressMode.ACCUMULATOR:
            ret = '{0} A'.format(cls.MNEMONIC)
        elif address_mode == AddressMode.ABSOLUTE:
            operand, address = AddressMode.calculate_operand(address_mode, bytez, mcu, memory)
            ret = '{0} ${1:04x}'.format(cls.MNEMONIC, address)
        elif address_mode == AddressMode.ABSOLUTE_X_INDEXED:
            operand, address = AddressMode.calculate_operand(address_mode, bytez, mcu, memory)
            ret = '{0} ${1:04x},X'.format(cls.MNEMONIC, address)
        elif address_mode == AddressMode.ABSOLUTE_Y_INDEXED:
            operand, address = AddressMode.calculate_operand(address_mode, bytez, mcu, memory)
            ret = '{0} ${1:04x},Y'.format(cls.MNEMONIC, address)
        elif address_mode == AddressMode.IMMEDIATE:
            ret = '{0} #${1:02x}'.format(cls.MNEMONIC, bytez[-1])
        elif address_mode == AddressMode.IMPLIED:
            ret = '{0}'.format(cls.MNEMONIC)
        elif address_mode == AddressMode.INDIRECT:
            operand, address = AddressMode.calculate_operand(address_mode, bytez, mcu, memory)
            ret = '{0} (${1:04x})'.format(cls.MNEMONIC, operand)
        elif address_mode == AddressMode.INDEXED_X_INDIRECT:
            operand, address = AddressMode.calculate_operand(address_mode, bytez, mcu, memory)
            ret = '{0} (${1:04x},X)'.format(cls.MNEMONIC, operand)
        elif address_mode == AddressMode.INDIRECT_Y_INDEXED:
            operand, address = AddressMode.calculate_operand(address_mode, bytez, mcu, memory)
            ret = '{0} (${1:04x},Y)'.format(cls.MNEMONIC, operand)
        elif address_mode == AddressMode.RELATIVE:
            operand, address = AddressMode.calculate_operand(address_mode, bytez, mcu, memory)
            ret = '{0} ${1:04x}'.format(cls.MNEMONIC, address)
        elif address_mode == AddressMode.ZEROPAGE:
            pass
        elif address_mode == AddressMode.ZEROPAGE_X_INDEXED:
            pass
        elif address_mode == AddressMode.ZEROPAGE_Y_INDEXED:
            pass

        else:
            ret = '{0}'.format(cls.MNEMONIC)

        return ret

    @classmethod
    def get_bytez(cls, opcode):
        """
        Get instruction bytes count.

        :param opcode: Instruction opcode.
        :return: Instruction bytes count.
        """
        _, bytez, _, _ = cls.INSTRUCTIONS[opcode]
        return bytez


class ADC(Instruction):  # pylint: disable=too-few-public-methods
    """Add Memory to Accumulator with Carry"""

    MNEMONIC = 'ADC'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x69: (AddressMode.IMMEDIATE, 2, 2, 0),
        0x65: (AddressMode.ZEROPAGE, 2, 3, 0),
        0x75: (AddressMode.ZEROPAGE_X_INDEXED, 2, 4, 0),
        0x6D: (AddressMode.ABSOLUTE, 3, 4, 0),
        0x7D: (AddressMode.ABSOLUTE_X_INDEXED, 3, 4, 1),
        0x79: (AddressMode.ABSOLUTE_Y_INDEXED, 3, 4, 1),
        0x61: (AddressMode.INDEXED_X_INDIRECT, 2, 6, 0),
        0x71: (AddressMode.INDIRECT_Y_INDEXED, 2, 5, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, _ = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        val = mcu.a.signed + operand + mcu.sr.C

        mcu.sr.C = 0
        mcu.sr.Z = 0
        mcu.sr.N = 0
        mcu.sr.V = 0

        mcu.sr.N = 1 if (val & (1 << 7)) > 0 else 0
        mcu.sr.Z = 1 if val == 0 else 0
        mcu.sr.C = 1 if val > 0xff else 0
        mcu.sr.V = 1 if (~(mcu.a.value ^ operand) & (mcu.a.value ^ val)) & 128 else 0

        mcu.a.value = val


class AND(Instruction):  # pylint: disable=too-few-public-methods
    """AND Memory with Accumulator"""

    MNEMONIC = 'AND'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x29: (AddressMode.IMMEDIATE, 2, 2, 0),
        0x25: (AddressMode.ZEROPAGE, 2, 3, 0),
        0x35: (AddressMode.ZEROPAGE_X_INDEXED, 2, 4, 0),
        0x2D: (AddressMode.ABSOLUTE, 3, 4, 0),
        0x3D: (AddressMode.ABSOLUTE_X_INDEXED, 3, 4, 1),
        0x39: (AddressMode.ABSOLUTE_Y_INDEXED, 3, 4, 1),
        0x21: (AddressMode.INDEXED_X_INDIRECT, 2, 6, 0),
        0x31: (AddressMode.INDIRECT_Y_INDEXED, 2, 5, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, _ = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        val = mcu.a.value & operand
        mcu.a.value = val

        mcu.sr.N = 1 if mcu.a.signed < 0 else 0
        mcu.sr.Z = 1 if val == 0 else 0


class ASL(Instruction):  # pylint: disable=too-few-public-methods
    """Shift Left One Bit (Memory or Accumulator)"""

    MNEMONIC = 'ASL'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x0A: (AddressMode.ACCUMULATOR, 1, 2, 0),
        0x06: (AddressMode.ZEROPAGE, 2, 5, 0),
        0x16: (AddressMode.ZEROPAGE_X_INDEXED, 2, 6, 0),
        0x0E: (AddressMode.ABSOLUTE, 3, 6, 0),
        0x1E: (AddressMode.ABSOLUTE_X_INDEXED, 3, 7, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        val = (operand << 1) & 0xff

        if address is not None:
            memory.write_byte(address, val)
        else:
            mcu.a.value = val

        mcu.sr.N = 1 if val > 127 else 0
        mcu.sr.Z = 1 if val == 0 else 0
        mcu.sr.C = 1 if val > 0xff else 0


class BCC(Instruction):  # pylint: disable=too-few-public-methods
    """Branch on Carry Clear"""

    MNEMONIC = 'BCC'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x90: (AddressMode.RELATIVE, 2, 3, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        if mcu.sr.C == 0:
            mcu.pc.value = address


class BCS(Instruction):  # pylint: disable=too-few-public-methods
    """Branch on Carry Set"""

    MNEMONIC = 'BCS'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xB0: (AddressMode.RELATIVE, 2, 3, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        if mcu.sr.C == 1:
            mcu.pc.value = address


class BEQ(Instruction):  # pylint: disable=too-few-public-methods
    """Branch on Carry Set"""

    MNEMONIC = 'BEQ'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xF0: (AddressMode.RELATIVE, 2, 3, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        if mcu.sr.Z == 1:
            mcu.pc.value = address


class BIT(Instruction):  # pylint: disable=too-few-public-methods
    """Test Bits in Memory with Accumulator"""

    MNEMONIC = 'BIT'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x24: (AddressMode.ZEROPAGE, 2, 3, 0),
        0x2C: (AddressMode.ABSOLUTE, 3, 4, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, _ = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        val = mcu.a.value & operand
        m7 = 1 if (val & (1 << 7)) > 0 else 0  # pylint: disable=invalid-name
        m6 = 1 if (val & (1 << 6)) > 0 else 0  # pylint: disable=invalid-name
        mcu.sr.N = m7
        mcu.sr.V = m6

        mcu.sr.Z = 1 if val == 0 else 0


class BMI(Instruction):  # pylint: disable=too-few-public-methods
    """Branch on Result Minus"""

    MNEMONIC = 'BMI'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x30: (AddressMode.RELATIVE, 2, 3, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        if mcu.sr.N == 1:
            mcu.pc.value = address


class BNE(Instruction):  # pylint: disable=too-few-public-methods
    """Branch on Result not Zero"""

    MNEMONIC = 'BNE'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xD0: (AddressMode.RELATIVE, 2, 3, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        if mcu.sr.Z == 0:
            mcu.pc.value = address


class BPL(Instruction):  # pylint: disable=too-few-public-methods
    """Branch on Result Plus"""

    MNEMONIC = 'BPL'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x10: (AddressMode.RELATIVE, 2, 3, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        if mcu.sr.N == 0:
            mcu.pc.value = address


class BRK(Instruction):  # pylint: disable=too-few-public-methods
    """Force Break"""

    MNEMONIC = 'BRK'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x00: (AddressMode.IMPLIED, 1, 7, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sr.B = 1


class BVC(Instruction):  # pylint: disable=too-few-public-methods
    """Branch on Overflow Clear"""

    MNEMONIC = 'BVC'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x50: (AddressMode.RELATIVE, 2, 3, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        if mcu.sr.V == 0:
            mcu.pc.value = address


class BVS(Instruction):  # pylint: disable=too-few-public-methods
    """Branch on Overflow Set"""

    MNEMONIC = 'BVS'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x70: (AddressMode.RELATIVE, 2, 3, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        if mcu.sr.V == 1:
            mcu.pc.value = address


class CLC(Instruction):  # pylint: disable=too-few-public-methods
    """Clear Carry Flag"""

    MNEMONIC = 'CLC'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x18: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sr.C = 0


class CLD(Instruction):  # pylint: disable=too-few-public-methods
    """Clear Decimal Mode"""

    MNEMONIC = 'CLD'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xD8: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sr.D = 0


class CLI(Instruction):  # pylint: disable=too-few-public-methods
    """Clear Interrupt Disable Bit"""

    MNEMONIC = 'CLI'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x58: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sr.I = 0


class CLV(Instruction):  # pylint: disable=too-few-public-methods
    """Clear Overflow Flag"""

    MNEMONIC = 'CLV'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xB8: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sr.V = 0


class CMP(Instruction):  # pylint: disable=too-few-public-methods
    """Compare Memory with Accumulator"""

    MNEMONIC = 'CMP'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xC9: (AddressMode.IMMEDIATE, 2, 2, 0),
        0xC5: (AddressMode.ZEROPAGE, 2, 3, 0),
        0xD5: (AddressMode.ZEROPAGE_X_INDEXED, 2, 4, 0),
        0xCD: (AddressMode.ABSOLUTE, 3, 4, 0),
        0xDD: (AddressMode.ABSOLUTE_X_INDEXED, 3, 4, 1),
        0xD9: (AddressMode.ABSOLUTE_Y_INDEXED, 3, 4, 1),
        0xC1: (AddressMode.INDEXED_X_INDIRECT, 2, 6, 0),
        0xD1: (AddressMode.INDIRECT_Y_INDEXED, 2, 5, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        val = mcu.a.value - operand

        mcu.sr.N, mcu.sr.Z, mcu.sr.C = 0, 0, 0

        mcu.sr.N = 1 if val & 128 > 0 else 0

        if val == 0:
            mcu.sr.Z = 1
            mcu.sr.C = 1
        elif operand < mcu.a.value:
            mcu.sr.C = 1


class CPX(Instruction):  # pylint: disable=too-few-public-methods
    """Compare Memory and Index X"""

    MNEMONIC = 'CPX'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xE0: (AddressMode.IMMEDIATE, 2, 2, 0),
        0xE4: (AddressMode.ZEROPAGE, 2, 3, 0),
        0xEC: (AddressMode.ABSOLUTE, 3, 4, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        val = mcu.x.value - operand

        mcu.sr.N, mcu.sr.Z, mcu.sr.C = 0, 0, 0

        mcu.sr.N = 1 if val & 128 > 0 else 0

        if val == 0:
            mcu.sr.Z = 1
            mcu.sr.C = 1
        elif operand < mcu.x.value:
            mcu.sr.C = 1


class CPY(Instruction):  # pylint: disable=too-few-public-methods
    """Compare Memory and Index Y"""

    MNEMONIC = 'CPY'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xC0: (AddressMode.IMMEDIATE, 2, 2, 0),
        0xC4: (AddressMode.ZEROPAGE, 2, 3, 0),
        0xCC: (AddressMode.ABSOLUTE, 3, 4, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        val = mcu.y.value - operand

        mcu.sr.N, mcu.sr.Z, mcu.sr.C = 0, 0, 0

        mcu.sr.N = 1 if val & 128 > 0 else 0

        if val == 0:
            mcu.sr.Z = 1
            mcu.sr.C = 1
        elif operand < mcu.y.value:
            mcu.sr.C = 1


class DEC(Instruction):  # pylint: disable=too-few-public-methods
    """Decrement Memory by One"""

    MNEMONIC = 'DEC'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xC6: (AddressMode.ZEROPAGE, 2, 5, 0),
        0xD6: (AddressMode.ZEROPAGE_X_INDEXED, 2, 6, 0),
        0xCE: (AddressMode.ABSOLUTE, 3, 3, 0),
        0xDE: (AddressMode.ABSOLUTE_X_INDEXED, 3, 7, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        val = operand - 1
        memory.write_byte(address, val)

        mcu.sr.N = 1 if val < 0 else 0
        mcu.sr.Z = 1 if val == 0 else 0


class DEX(Instruction):  # pylint: disable=too-few-public-methods
    """Decrement Index X by One"""

    MNEMONIC = 'DEX'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xCA: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """

        val = mcu.x.value - 1
        mcu.x.value = val

        mcu.sr.N = 1 if mcu.x.signed < 0 else 0
        mcu.sr.Z = 1 if val == 0 else 0


class DEY(Instruction):  # pylint: disable=too-few-public-methods
    """Decrement Index Y by One"""

    MNEMONIC = 'DEY'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x88: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """

        val = mcu.y.value - 1
        mcu.y.value = val

        mcu.sr.N = 1 if mcu.y.signed < 0 else 0
        mcu.sr.Z = 1 if val == 0 else 0


class EOR(Instruction):  # pylint: disable=too-few-public-methods
    """Exclusive-OR Memory with Accumulator"""

    MNEMONIC = 'EOR'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x49: (AddressMode.IMMEDIATE, 2, 2, 0),
        0x45: (AddressMode.ZEROPAGE, 2, 3, 0),
        0x55: (AddressMode.ZEROPAGE_X_INDEXED, 2, 4, 0),
        0x4D: (AddressMode.ABSOLUTE, 3, 4, 0),
        0x5D: (AddressMode.ABSOLUTE_X_INDEXED, 3, 4, 1),
        0x59: (AddressMode.ABSOLUTE_Y_INDEXED, 3, 4, 1),
        0x41: (AddressMode.INDEXED_X_INDIRECT, 2, 6, 0),
        0x51: (AddressMode.INDIRECT_Y_INDEXED, 2, 5, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, _ = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        val = mcu.a.value ^ operand
        mcu.a.value = val

        mcu.sr.N = 1 if mcu.a.signed < 0 else 0
        mcu.sr.Z = 1 if val == 0 else 0


class INC(Instruction):  # pylint: disable=too-few-public-methods
    """Increment Memory by One"""

    MNEMONIC = 'INC'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xE6: (AddressMode.ZEROPAGE, 2, 5, 0),
        0xF6: (AddressMode.ZEROPAGE_X_INDEXED, 2, 6, 0),
        0xEE: (AddressMode.ABSOLUTE, 3, 6, 0),
        0xFE: (AddressMode.ABSOLUTE_X_INDEXED, 3, 7, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        val = operand + 1
        memory.write_byte(address, val)

        mcu.sr.N = 1 if val < 0 else 0
        mcu.sr.Z = 1 if val == 0 else 0


class INX(Instruction):  # pylint: disable=too-few-public-methods
    """Increment Index X by One"""

    MNEMONIC = 'INX'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xE8: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        val = mcu.x.value + 1
        mcu.x.value = val

        mcu.sr.N = 1 if mcu.x.signed < 0 else 0
        mcu.sr.Z = 1 if val == 0 else 0


class INY(Instruction):  # pylint: disable=too-few-public-methods
    """Increment Index Y by One"""

    MNEMONIC = 'INY'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xC8: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        val = mcu.y.value + 1
        mcu.y.value = val

        mcu.sr.N = 1 if mcu.y.signed < 0 else 0
        mcu.sr.Z = 1 if val == 0 else 0


class JMP(Instruction):  # pylint: disable=too-few-public-methods
    """Jump to New Location"""

    MNEMONIC = 'JMP'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x4C: (AddressMode.ABSOLUTE, 3, 3, 0),
        0x6C: (AddressMode.INDIRECT, 3, 5, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        _, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        mcu.pc.value = address


class JSR(Instruction):  # pylint: disable=too-few-public-methods
    """Jump to New Location Saving Return Address"""

    MNEMONIC = 'JSR'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x20: (AddressMode.ABSOLUTE, 3, 6, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        ret_address = mcu.pc.value - 1
        low = ret_address & 0xff
        high = (ret_address >> 8) & 0xff

        memory.write_byte(mcu.sp.value + mcu.sp_base, high)
        mcu.sp.value = (mcu.sp.value - 1) & 0xff
        memory.write_byte(mcu.sp.value + mcu.sp_base, low)
        mcu.sp.value = (mcu.sp.value - 1) & 0xff

        mcu.pc.value = address


class LDA(Instruction):  # pylint: disable=too-few-public-methods
    """Load Accumulator with Memory"""

    MNEMONIC = 'LDA'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xA9: (AddressMode.IMMEDIATE, 2, 2, 0),
        0xA5: (AddressMode.ZEROPAGE, 2, 3, 0),
        0xB5: (AddressMode.ZEROPAGE_X_INDEXED, 2, 4, 0),
        0xAD: (AddressMode.ABSOLUTE, 3, 4, 0),
        0xBD: (AddressMode.ABSOLUTE_X_INDEXED, 3, 4, 1),
        0xB9: (AddressMode.ABSOLUTE_Y_INDEXED, 3, 4, 1),
        0xA1: (AddressMode.INDEXED_X_INDIRECT, 2, 6, 0),
        0xB1: (AddressMode.INDIRECT_Y_INDEXED, 2, 5, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        mcu.a.value = operand

        mcu.sr.N = 1 if mcu.a.signed < 0 else 0
        mcu.sr.Z = 1 if operand == 0 else 0


class LDX(Instruction):  # pylint: disable=too-few-public-methods
    """Load Index X with Memory"""

    MNEMONIC = 'LDX'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xA2: (AddressMode.IMMEDIATE, 2, 2, 0),
        0xA6: (AddressMode.ZEROPAGE, 2, 3, 0),
        0xB6: (AddressMode.ZEROPAGE_Y_INDEXED, 2, 4, 0),
        0xAE: (AddressMode.ABSOLUTE, 3, 4, 0),
        0xBE: (AddressMode.ABSOLUTE_Y_INDEXED, 3, 4, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, _ = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        mcu.x.value = operand

        mcu.sr.N = 1 if mcu.x.signed < 0 else 0
        mcu.sr.Z = 1 if operand == 0 else 0


class LDY(Instruction):  # pylint: disable=too-few-public-methods
    """Load Index Y with Memory"""

    MNEMONIC = 'LDY'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xA0: (AddressMode.IMMEDIATE, 2, 2, 0),
        0xA4: (AddressMode.ZEROPAGE, 2, 3, 0),
        0xB4: (AddressMode.ZEROPAGE_Y_INDEXED, 2, 4, 0),
        0xAC: (AddressMode.ABSOLUTE, 3, 4, 0),
        0xBC: (AddressMode.ABSOLUTE_Y_INDEXED, 3, 4, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, _ = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        mcu.y.value = operand

        mcu.sr.N = 1 if mcu.y.signed < 0 else 0
        mcu.sr.Z = 1 if operand == 0 else 0


class LSR(Instruction):  # pylint: disable=too-few-public-methods
    """Shift One Bit Right (Memory or Accumulator)"""

    MNEMONIC = 'LSR'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x4A: (AddressMode.ACCUMULATOR, 1, 2, 0),
        0x46: (AddressMode.ZEROPAGE, 2, 5, 0),
        0x56: (AddressMode.ZEROPAGE_X_INDEXED, 2, 6, 0),
        0x4E: (AddressMode.ABSOLUTE, 3, 6, 0),
        0x5E: (AddressMode.ABSOLUTE_X_INDEXED, 3, 7, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        carry = operand & 0x01
        val = operand >> 1

        if opcode == 0x4A:
            mcu.a.value = val
        else:
            memory.write_byte(address, val)

        mcu.sr.Z = 1 if val == 0 else 0
        mcu.sr.C = carry


class NOP(Instruction):  # pylint: disable=too-few-public-methods
    """No Operation"""

    MNEMONIC = 'NOP'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xEA: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        pass


class ORA(Instruction):  # pylint: disable=too-few-public-methods
    """OR Memory with Accumulator"""

    MNEMONIC = 'ORA'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x09: (AddressMode.IMMEDIATE, 2, 2, 0),
        0x05: (AddressMode.ZEROPAGE, 2, 3, 0),
        0x15: (AddressMode.ZEROPAGE_X_INDEXED, 2, 4, 0),
        0x0D: (AddressMode.ABSOLUTE, 3, 4, 0),
        0x1D: (AddressMode.ABSOLUTE_X_INDEXED, 3, 4, 1),
        0x19: (AddressMode.ABSOLUTE_Y_INDEXED, 3, 4, 1),
        0x01: (AddressMode.INDEXED_X_INDIRECT, 2, 6, 0),
        0x11: (AddressMode.INDIRECT_Y_INDEXED, 2, 5, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, _ = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        val = mcu.a.value | operand
        mcu.a.value = val

        mcu.sr.N = 1 if mcu.a.signed < 0 else 0
        mcu.sr.Z = 1 if val == 0 else 0


class PHA(Instruction):  # pylint: disable=too-few-public-methods
    """Push Accumulator on Stack"""

    MNEMONIC = 'PHA'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x48: (AddressMode.IMPLIED, 1, 3, 0),
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        memory.write_byte(mcu.sp.value + mcu.sp_base, mcu.a.value)
        mcu.sp.value = (mcu.sp.value - 1) & 0xff


class PHP(Instruction):  # pylint: disable=too-few-public-methods
    """Push Processor Status on Stack"""

    MNEMONIC = 'PHP'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x08: (AddressMode.IMPLIED, 1, 3, 0),
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        memory.write_byte(mcu.sp.value + mcu.sp_base, mcu.sr.value)
        mcu.sp.value = (mcu.sp.value - 1) & 0xff


class PLA(Instruction):  # pylint: disable=too-few-public-methods
    """Pull Accumulator from Stack"""

    MNEMONIC = 'PLA'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x68: (AddressMode.IMPLIED, 1, 4, 0),
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sp.value = (mcu.sp.value + 1) & 0xff
        mcu.a.value = memory.read_byte(mcu.sp.value + mcu.sp_base)

        mcu.sr.N = 1 if mcu.a.signed < 0 else 0
        mcu.sr.Z = 1 if mcu.a.value == 0 else 0


class PLP(Instruction):  # pylint: disable=too-few-public-methods
    """Pull Processor Status from Stack"""

    MNEMONIC = 'PLP'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x28: (AddressMode.IMPLIED, 1, 4, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sp.value = (mcu.sp.value + 1) & 0xff
        mcu.sr.value = memory.read_byte(mcu.sp.value + mcu.sp_base)


class ROL(Instruction):  # pylint: disable=too-few-public-methods
    """Rotate One Bit Left (Memory or Accumulator)"""

    MNEMONIC = 'ROL'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x2A: (AddressMode.ACCUMULATOR, 1, 2, 0),
        0x26: (AddressMode.ZEROPAGE, 2, 5, 0),
        0x36: (AddressMode.ZEROPAGE_X_INDEXED, 2, 6, 0),
        0x2E: (AddressMode.ABSOLUTE, 3, 6, 0),
        0x3E: (AddressMode.ABSOLUTE_X_INDEXED, 3, 7, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        c_flag = (operand & 255) >> 7
        operand = (((operand << 1) | mcu.sr.C) & 0xff)

        if address is not None:
            memory.write_byte(address, operand)
        else:
            mcu.a.value = operand

        mcu.sr.N = 1 if to_signed_byte(operand) < 0 else 0
        mcu.sr.Z = 1 if operand == 0 else 0
        mcu.sr.C = c_flag


class ROR(Instruction):  # pylint: disable=too-few-public-methods
    """Rotate One Bit Right (Memory or Accumulator)"""

    MNEMONIC = 'ROR'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x6A: (AddressMode.ACCUMULATOR, 1, 2, 0),
        0x66: (AddressMode.ZEROPAGE, 2, 5, 0),
        0x76: (AddressMode.ZEROPAGE_X_INDEXED, 2, 6, 0),
        0x6E: (AddressMode.ABSOLUTE, 3, 6, 0),
        0x7E: (AddressMode.ABSOLUTE_X_INDEXED, 3, 7, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        c_flag = (operand & 1)
        operand = ((operand >> 1) | (mcu.sr.C << 7))

        if address is not None:
            memory.write_byte(address, operand)
        else:
            mcu.a.value = operand

        mcu.sr.N = 1 if operand < 0 else 0
        mcu.sr.Z = 1 if operand == 0 else 0
        mcu.sr.C = c_flag


class RTI(Instruction):  # pylint: disable=too-few-public-methods
    """Return from Interrupt"""

    MNEMONIC = 'RTI'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x40: (AddressMode.IMPLIED, 1, 6, 0),
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sr.value = memory.read_byte(mcu.sp.value)
        mcu.sp.value = mcu.sp.value + 1

        mcu.pc.value = memory.read_byte(mcu.sp.value)
        mcu.sp.value = mcu.sp.value + 1

        mcu.sr.B = 1


class RTS(Instruction):  # pylint: disable=too-few-public-methods
    """Return from Subroutine"""

    MNEMONIC = 'RTS'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x60: (AddressMode.IMPLIED, 1, 6, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sp.value = (mcu.sp.value + 1) & 0xff
        val = memory.read_byte(mcu.sp.value + mcu.sp_base)
        mcu.sp.value = (mcu.sp.value + 1) & 0xff
        val |= memory.read_byte(mcu.sp.value + mcu.sp_base) << 8

        mcu.pc.value = val + 1


class SBC(Instruction):  # pylint: disable=too-few-public-methods
    """Subtract Memory from Accumulator with Borrow"""

    MNEMONIC = 'SBC'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xE9: (AddressMode.IMMEDIATE, 2, 2, 0),
        0xE5: (AddressMode.ZEROPAGE, 2, 3, 0),
        0xF5: (AddressMode.ZEROPAGE_X_INDEXED, 2, 4, 0),
        0xED: (AddressMode.ABSOLUTE, 3, 4, 0),
        0xFD: (AddressMode.ABSOLUTE_X_INDEXED, 3, 4, 1),
        0xF9: (AddressMode.ABSOLUTE_Y_INDEXED, 3, 4, 1),
        0xE1: (AddressMode.INDEXED_X_INDIRECT, 2, 6, 0),
        0xF1: (AddressMode.INDIRECT_Y_INDEXED, 2, 5, 1)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        operand, _ = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        val = mcu.a.signed + (~operand & 0xff) + mcu.sr.C

        mcu.sr.C = 0
        mcu.sr.Z = 0
        mcu.sr.N = 0
        mcu.sr.V = 0

        mcu.sr.N = 1 if (val & (1 << 7)) > 0 else 0
        mcu.sr.Z = 1 if (val & 0xff == 0) else 0
        mcu.sr.C = 1 if val > 0xff else 0
        mcu.sr.V = 1 if (~(mcu.a.value ^ operand) & (mcu.a.value ^ val)) & 128 else 0

        mcu.a.value = val


class SEC(Instruction):  # pylint: disable=too-few-public-methods
    """Set Carry Flag"""

    MNEMONIC = 'SEC'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x38: (AddressMode.IMPLIED, 1, 2, 0),
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sr.C = 1


class SED(Instruction):  # pylint: disable=too-few-public-methods
    """Set Decimal Flag"""

    MNEMONIC = 'SED'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xF8: (AddressMode.IMPLIED, 1, 2, 0),
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sr.D = 1


class SEI(Instruction):  # pylint: disable=too-few-public-methods
    """Set Interrupt Disable Status"""

    MNEMONIC = 'SEI'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x78: (AddressMode.IMPLIED, 1, 2, 0),
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sr.I = 1


class STA(Instruction):  # pylint: disable=too-few-public-methods
    """Store Accumulator in Memory"""

    MNEMONIC = 'STA'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x85: (AddressMode.ZEROPAGE, 2, 3, 0),
        0x95: (AddressMode.ZEROPAGE_X_INDEXED, 2, 4, 0),
        0x8D: (AddressMode.ABSOLUTE, 3, 4, 0),
        0x9D: (AddressMode.ABSOLUTE_X_INDEXED, 3, 5, 0),
        0x99: (AddressMode.ABSOLUTE_Y_INDEXED, 3, 5, 0),
        0x81: (AddressMode.INDEXED_X_INDIRECT, 2, 6, 0),
        0x91: (AddressMode.INDIRECT_Y_INDEXED, 2, 6, 0),
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        _, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        memory.write_byte(address, mcu.a.value)


class STX(Instruction):  # pylint: disable=too-few-public-methods
    """Store Index X in Memory"""

    MNEMONIC = 'STX'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x86: (AddressMode.ZEROPAGE, 2, 3, 0),
        0x96: (AddressMode.ZEROPAGE_Y_INDEXED, 2, 4, 0),
        0x8E: (AddressMode.ABSOLUTE, 3, 4, 0),
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        _, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        memory.write_byte(address, mcu.x.value)


class STY(Instruction):  # pylint: disable=too-few-public-methods
    """Sore Index Y in Memory"""

    MNEMONIC = 'STY'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x84: (AddressMode.ZEROPAGE, 2, 3, 0),
        0x94: (AddressMode.ZEROPAGE_X_INDEXED, 2, 4, 0),
        0x8C: (AddressMode.ABSOLUTE, 3, 4, 0),
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mode, _, _, _ = cls.INSTRUCTIONS[opcode]
        _, address = AddressMode.calculate_operand(mode, bytez, mcu, memory)

        memory.write_byte(address, mcu.y.value)


class TAX(Instruction):  # pylint: disable=too-few-public-methods
    """Transfer Accumulator to Index X"""

    MNEMONIC = 'TAX'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xAA: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.x.value = mcu.a.value

        mcu.sr.N = 1 if mcu.x.signed < 0 else 0
        mcu.sr.Z = 1 if mcu.x.value == 0 else 0


class TAY(Instruction):  # pylint: disable=too-few-public-methods
    """Transfer Accumulator to Index Y"""

    MNEMONIC = 'TAY'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xA8: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.y.value = mcu.a.value

        mcu.sr.N = 1 if mcu.y.signed < 0 else 0
        mcu.sr.Z = 1 if mcu.y.value == 0 else 0


class TSX(Instruction):  # pylint: disable=too-few-public-methods
    """Transfer Stack Pointer to Index X"""

    MNEMONIC = 'TSX'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0xBA: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.x.value = mcu.sp.value

        mcu.sr.N = 1 if mcu.x.signed < 0 else 0
        mcu.sr.Z = 1 if mcu.x.value == 0 else 0


class TXA(Instruction):  # pylint: disable=too-few-public-methods
    """Transfer Index X to Accumulator"""

    MNEMONIC = 'TXA'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x8A: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.a.value = mcu.x.value

        mcu.sr.N = 1 if mcu.a.signed < 0 else 0
        mcu.sr.Z = 1 if mcu.a.value == 0 else 0


class TXS(Instruction):  # pylint: disable=too-few-public-methods
    """Transfer Index X to Stack Register"""

    MNEMONIC = 'TXS'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x9A: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.sp.value = mcu.x.value


class TYA(Instruction):  # pylint: disable=too-few-public-methods
    """Transfer Index Y to Accumulator"""

    MNEMONIC = 'TYA'
    # Dict of tuples (#address_mode, #bytes, #cycles, #page_boundary_cycles) keyed by #opcode
    INSTRUCTIONS = {
        0x98: (AddressMode.IMPLIED, 1, 2, 0)
    }

    @classmethod
    def execute(cls, opcode, bytez, mcu, memory):  # pylint: disable=unused-argument
        """
        Execute command.

        :param opcode: Command opcode.
        :param bytez: Command bytes.
        :param mcu: MCU instance.
        :param memory: Memory instance.
        :return: Nothing.
        """
        mcu.a.value = mcu.y.value

        mcu.sr.N = 1 if mcu.a.signed < 0 else 0
        mcu.sr.Z = 1 if mcu.a.value == 0 else 0



INSTRUCTIONS = {}
clazz = [ADC, AND, ASL, BCC, BCS, BEQ, BIT, BMI, BNE, BPL, BRK, BVC, BVS, CLC,
         CLD, CLI, CLV, CMP, CPX, CPY, DEC, DEX, DEY, EOR, INC, INX, INY, JMP,
         JSR, LDA, LDX, LDY, LSR, NOP, ORA, PHA, PHP, PLA, PLP, ROL, ROR, RTI,
         RTS, SBC, SEC, SED, SEI, STA, STX, STY, TAX, TAY, TSX, TXA, TXS, TYA]

for c in clazz:
    for k in c.INSTRUCTIONS:
        INSTRUCTIONS[k] = c



if __name__ == '__main__':
    pass
