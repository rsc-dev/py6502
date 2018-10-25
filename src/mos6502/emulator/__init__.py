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
        self.memory = Memory()
        self.processor = MCU()

    def load(self, address, data):
        """
        Load data into memory.

        :param address: Memory address where data will be loaded.
        :param data: Data to be loaded.
        :return: Nothing.
        """
        self.memory.load(address, data)

    def step(self):
        """
        Run single step.

        :return: Nothing.
        """
        if self.processor.sr.B == 0:
            # 1. fetch
            pc = self.processor.pc.value   # pylint: disable=invalid-name
            opcode = self.memory.read_byte(pc)

            # 2. decode
            opcode_class = INSTRUCTIONS[opcode]
            # TODO: this should be done in execute
            bytez = opcode_class.get_bytez(opcode)
            data = self.memory._memory[pc + 1:pc + bytez]  # pylint: disable=protected-access

            log = '{pc:04x} {op:02x}'.format(pc=pc, op=opcode)
            temp = '{}' + ' {:02x}' * len(data) + '   ' * (2-len(data))
            log = temp.format(log, *data)
            log = '{log} {mnemonic}'.format(log=log, mnemonic=opcode_class.MNEMONIC)
            log = '{log} A:{A:02x} X:{X:02x} Y:{Y:02x}'.format(
                log=log, A=self.processor.a.value, X=self.processor.x.value, Y=self.processor.y.value)
            print(log)
            print('\tNV-BDIZC')
            sr = self.processor.sr
            print('\t{0}{1}1{2}{3}{4}{5}{6}'.format(sr.N, sr.V, sr.B, sr.D, sr.I, sr.Z, sr.C))


            # 3. execute
            self.processor.pc.value += bytez
            opcode_class.execute(opcode, data, self.processor, self.memory)

    def run(self):
        """
        Run emulator loop.

        :return: Nothing.
        """
        while self.processor.sr.B == 0:
            self.step()


if __name__ == '__main__':
    pass
