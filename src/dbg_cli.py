import cmd

from mos6502 import emulator as e


class DbgCli(cmd.Cmd):

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = 'py6502>'

        self.do_reset(None)

    def do_mcu(self, _):
        """Show mcu registers."""
        print()
        print('\t--- MCU ---')
        print('\tA=0x{:02x}'.format(self.emulator.processor.a.value))
        print('\tX=0x{:02x}'.format(self.emulator.processor.x.value))
        print('\tY=0x{:02x}'.format(self.emulator.processor.y.value))
        print()
        print('\tSP=0x{:02x}'.format(self.emulator.processor.sp.value))
        print('\tPC=0x{:04x}'.format(self.emulator.processor.pc.value))
        print()
        sr = self.emulator.processor.sr
        print('\tSR=0x{:02x}'.format(sr.value))
        print('\tNV-BDIZC')
        print('\t{0}{1}1{2}{3}{4}{5}{6}'.format(sr.N, sr.V, sr.B, sr.D, sr.I, sr.Z, sr.C))
        print()

    def do_memory(self, line):
        try:
            address, length = line.split()
            address = int(address, 16)
            length = int(length, 16)

            assert address < self.emulator.memory.SIZE

            print()
            lines = int(length / 16)
            for i in range(0, lines + 1):
                bytez = 16 if (i * 16 + 16) < length else length - i * 16
                mem = self.emulator.memory._memory[address + (i * 16):address + (i * 16) + bytez + 1]

                if len(mem) >= 0:
                    s = '{:04x}: ' + '{:02x} ' * len(mem)
                    print(s.format(address + i * 16, *mem))
            print()
        except ValueError:
            print('[!] Usage: memory <address> <length>')

    def do_load(self, line):
        s = line.split()

        address = int(s[0], 16)
        data = [int(b, 16) for b in s[1:]]

        self.emulator.memory.load(address, data)

    def do_file(self, file_name):
        with open(file_name, 'rb') as fh:
            data = fh.read()

        self.emulator.memory.load(0x00, data)

    def do_step(self, _):
        """Execute single step."""
        try:
            self.emulator.step()
        except KeyError as ker:
            print('Key error!')

    def do_pc(self, pc):
        """Set PC registry value."""
        pc = int(pc, 16)
        self.emulator.processor.pc.value = pc

    def do_run(self, _):
        """Run till SR.B = 1"""
        self.emulator.run()

    def do_reset(self, _):
        self.emulator = e.Emulator()

    def do_exit(self, _):
        """Exit debugger."""
        return True


if __name__ == '__main__':
    dbgCli = DbgCli()
    dbgCli.cmdloop()
