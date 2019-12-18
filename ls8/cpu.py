"""CPU functionality."""

import sys
import re

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
POP = 0b01000110
PUSH= 0b01000101



class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.op_table = {
            MUL: lambda a, b: self.alu('MUL', a, b),
            LDI: lambda a, b: self.reg_write(a, b),
            PRN: lambda a, b: print(self.reg[a]),
            POP: self.pop_stack,
            PUSH: self.push_stack
        }
        self.PC = 0
        self.SP = 0xF4
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = self.SP


    def load(self, program):
        """Load a program into memory."""
        address = 0
        with open(f"examples/{program}.ls8", 'r') as f:
            for line in f:
                if instruction := re.match(r"(\d+)(?=\D)", line):
                    self.ram_write(address, int(instruction[0], 2))
                    address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            # self.fl,
            # self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def reg_write(self, register, value):
        self.reg[register] = value

    def pop_stack(self, reg_address, _):
        self.reg[reg_address] = self.ram_read(self.SP)
        self.SP += 1

    def push_stack(self, reg_address, _):
        self.SP -= 1
        self.ram_write(self.SP, self.reg[reg_address])

    def run(self):
        """Run the CPU."""
        halted = False
        while not halted:
            IR = self.ram_read(self.PC)
            operand_a = self.ram_read(self.PC + 1)
            operand_b = self.ram_read(self.PC + 2)

            if IR in self.op_table:
                self.op_table[IR](operand_a, operand_b)
                operands = self.ram[self.PC] >> 6
                self.PC += operands + 1
            elif IR == HLT:
                halted = True
            else:
                print('Unknown instruction')
                sys.exit(1)
