#!/usr/bin/env python

"""6502 emulator"""

__author__ = 'Radoslaw Matusiak'
__copyright__ = 'Copyright (c) 2018 Radoslaw Matusiak'
__license__ = 'MIT'


from mos6502.assembly import INSTRUCTIONS  # pylint: disable=import-error
from mos6502.memory import Memory  # pylint: disable=import-error
from mos6502.processor import MCU  # pylint: disable=import-error


class Emulator(object):
    """6502 Emulator"""

    def __init__(self):
        self._memory = Memory()
        self._processor = MCU()

    def load(self, address, data):
        """
        Load data into memory.

        :param address: Memory address where data will be loaded.
        :param data: Data to be loaded.
        :return: Nothing.
        """
        self._memory.load(address, data)

    def step(self):
        """
        Run single step.

        :return: Nothing.
        """
        # 1. fetch
        self._processor.sr.B = 1
        pc = self._processor.pc.value   # pylint: disable=invalid-name
        opcode = self._memory.read_byte(pc)

        # 2. decode
        opcode_class = INSTRUCTIONS[opcode]
        # TODO: this should be done in execute
        bytez = opcode_class.get_bytez(opcode)

        data = self._memory._memory[pc + 1:pc + bytez]  # pylint: disable=protected-access

        log = '${pc:04x}  {op:02x}'.format(pc=pc, op=opcode)
        temp = '{}' + ' {:02x}' * len(data) + '   ' * (2-len(data))
        log = temp.format(log, *data)

        disasm = opcode_class.disassm(opcode, self._processor, self._memory, data)

        log = '{log}  {disasm}'.format(log=log, disasm=disasm)
        #log = '{log} A:{A:02x} X:{X:02x} Y:{Y:02x}'.format(
        #    log=log, A=self.processor.a.value, X=self.processor.x.value, Y=self.processor.y.value)
        print(log)
        print()
        print('       PC  AC XR YR SP NV-BDIZC')
        sr = self._processor.sr
        print('6502: {0:04x} {1:02x} {2:02x} {3:02x} {4:02x} {5}{6}{7}{8}{9}{10}{11}{12}'.format(
            pc, self._processor.a.value, self._processor.x.value,
            self._processor.y.value, self._processor.sp.value, sr.N, sr.V, sr._get_bit_value(5), sr.B, sr.D, sr.I, sr.Z, sr.C))

        # 3. execute
        self._processor.pc.value += bytez
        opcode_class.execute(opcode, data, self._processor, self._memory)

    def run(self):
        """
        Run emulator loop.

        :return: Nothing.
        """
        while self._memory.read_byte(self._processor.pc.value) != 0x00:  # BRK
            self.step()

        print('BRK at {0}'.format(self._processor.pc.value))


if __name__ == '__main__':
    pass
