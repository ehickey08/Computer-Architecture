"""CPU functionality."""

import sys
import re

# Simple Start and Halt instructions
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001

# ALU Math
ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011
MOD = 0b10100100
DEC = 0b01100110
INC = 0b01100101

# Stack implementation
POP = 0b01000110
PUSH = 0b01000101

# Subroutine implementation
CALL = 0b01010000
RET = 0b00010001

# Sprint
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

# Bitwise Stretch
AND = 0b10101000
OR = 0b10101010
XOR = 0b10101011
NOT = 0b01101001
SHL = 0b10101100
SHR = 0b10101101

# Interrupt Stretch
INT = 0b01010010
IRET = 0b00010011

# Additional Commands
JGE = 0b01011010
JGT = 0b01010111
JLE = 0b01011001
JLT = 0b01011000
LD = 0b10000011
NOP = 0b00000000
PRA = 0b01001000
ST = 0b10000100


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.op_table = {
            LDI: lambda a, b: self.reg_write(a, b),
            PRN: lambda a, b: print(self.reg[a]),
            # ---ALU---
            ADD: lambda a, b: self.alu('ADD', a, b),
            SUB: lambda a, b: self.alu('SUB, a, b'),
            MUL: lambda a, b: self.alu('MUL', a, b),
            DIV: lambda a, b: self.alu('DIV', a, b),
            MOD: lambda a, b: self.alu('MOD', a, b),
            DEC: lambda a, b: self.alu('DEC', a, b),
            INC: lambda a, b: self.alu('INC', a, b),
            # ---Stack---
            POP: lambda a, _: self.pop_stack(a),
            PUSH: lambda a, _: self.push_stack(a),
            # ---Subroutines---
            CALL: lambda a, _: self.call(a),
            RET: lambda *_args: self.ret(),
            # ---Sprint: Loop Logic
            CMP: lambda a, b: self.alu('CMP', a, b),
            JMP: lambda a, _: self.set_pc(a),
            JEQ: lambda a, b: self.comparator('eq', a),
            JNE: lambda a, b: self.comparator('ne', a),
            # Stretch: Bitwise Logic
            AND: lambda a, b: self.alu('AND', a, b),
            OR: lambda a, b: self.alu('OR', a, b),
            XOR: lambda a, b: self.alu('XOR', a, b),
            NOT: lambda a, b: self.alu('NOT', a, b),
            SHL: lambda a, b: self.alu('SHL', a, b),
            SHR: lambda a, b: self.alu('SHR', a, b),
            # Additional Commands
            JGE: lambda a, b: self.comparator('ge', a),
            JGT: lambda a, b: self.comparator('gt', a),
            JLE: lambda a, b: self.comparator('le', a),
            JLT: lambda a, b: self.comparator('lt', a),
            LD: lambda a, b: self.ld(a, b),
            ST: lambda a, b: self.st(a, b),
            PRA: lambda a, b: print(chr(self.reg[a]), end='')
        }
        self.PC = 0
        self.FL = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.IM = 5
        self.IS = 6
        self.SP = 7
        self.reg[self.SP] = 0xF4

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

        # MATH OPERATIONS
        def add(reg_a, reg_b):
            self.reg[reg_a] += self.reg[reg_b]

        def sub(reg_a, reg_b):
            self.reg[reg_a] -= self.reg[reg_b]

        def mul(reg_a, reg_b):
            self.reg[reg_a] *= self.reg[reg_b]

        def div(reg_a, reg_b):
            self.reg[reg_a] /= self.reg[reg_b]

        def mod(reg_a, reg_b):
            self.reg[reg_a] %= self.reg[reg_b]

        def inc(reg_a, _):
            self.reg[reg_a] += 1

        def dec(reg_a, _):
            self.reg[reg_a] -= 1

        # BITWISE OPERATIONS
        def and_op(reg_a, reg_b):
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]

        def or_op(reg_a, reg_b):
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]

        def xor_op(reg_a, reg_b):
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]

        def not_op(reg_a, _):
            self.reg[reg_a] = ~self.reg[reg_a]

        def shl_op(reg_a, reg_b):
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]

        def shr_op(reg_a, reg_b):
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]

        alu_math_ops = {
            "ADD": add,
            "SUB": sub,
            "MUL": mul,
            "DIV": div,
            'MOD': mod,
            "DEC": dec,
            "INC": inc
        }

        alu_bit_ops = {
            "AND": and_op,
            "OR": or_op,
            'XOR': xor_op,
            'NOT': not_op,
            'SHL': shl_op,
            'SHR': shr_op,
        }

        try:
            if op in alu_math_ops:
                alu_math_ops[op](reg_a, reg_b)
            elif op in alu_bit_ops:
                alu_bit_ops[op](reg_a, reg_b)
            elif op == 'CMP':
                self.FL = 0b00000000
                if self.reg[reg_a] == self.reg[reg_b]:
                    self.FL = 0b00000001
                elif self.reg[reg_a] < self.reg[reg_b]:
                    self.FL = 0b00000100
                else:
                    self.FL = 0b00000010
        except:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X %02X| %02X %02X %02X |" % (
            self.PC,
            self.FL,
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

    def pop_stack(self, reg_address):
        self.reg[reg_address] = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1

    def push_stack(self, reg_address):
        self.reg[self.SP] -= 1
        self.ram_write(self.reg[self.SP], self.reg[reg_address])

    def call(self, reg_address):
        self.reg[self.SP] -= 1
        self.ram_write(self.reg[self.SP], self.PC + 2)
        self.PC = self.reg[reg_address]

    def ret(self):
        self.PC = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1

    def set_pc(self, reg_a):
        self.PC = self.reg[reg_a]

    def comparator(self, test, reg_a):
        masks = {
            'eq': 0b1,
            'ne': 0b1,
            'ge': 0b11,
            'gt': 0b10,
            'le': 0b101,
            'lt': 0b100,
        }
        flag = self.FL & masks[test]
        if flag and test != 'ne':
            self.PC = self.reg[reg_a]
        elif test == 'ne' and flag == 0:
            self.PC = self.reg[reg_a]
        else:
            self.PC += 2

    def ld(self, reg_a, reg_b):
        self.reg[reg_a] = self.ram_read(self.reg[reg_b])

    def st(self, reg_a, reg_b):
        self.ram_write(self.reg[reg_a], self.reg[reg_b])

    def check_interrupts(self):
        maskedInterrupts = self.reg[self.IM] & self.reg[self.IS]
        MI_str = f"{maskedInterrupts:08b}"
        set_bit = None
        for i in range(7, -1, -1):
            if MI_str[i]:
                set_bit = i
                break
        if set_bit is not None:
            self.reg[self.IS]
            self.push_stack(self.PC)
            self.push_stack(self.FL)
            for i in range(7):
                self.push_stack(self.reg[i])

    def run(self):
        """Run the CPU."""
        halted = False
        while not halted:
            IR = self.ram_read(self.PC)
            operand_a = self.ram_read(self.PC + 1)
            operand_b = self.ram_read(self.PC + 2)

            if IR in self.op_table:
                self.op_table[IR](operand_a, operand_b)
                operands = IR >> 6
                set_directly = (IR & 0b10000) >> 4
                if not set_directly:
                    self.PC += operands + 1
            elif IR == HLT:
                halted = True
            elif IR == NOP:
                continue
            else:
                print('Unknown instruction')
                sys.exit(1)
