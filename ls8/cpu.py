"""CPU functionality."""

import sys
import re
from datetime import datetime
import msvcrt

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
            # Sprint: Loop Logic
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
            # Stretch: Interrupts
            INT: lambda a, b: self.interrupt(a, b),
            IRET: lambda a, b: self.inter_ret(),
            # Additional Commands
            # ---Comparing Logic---
            JGE: lambda a, b: self.comparator('ge', a),
            JGT: lambda a, b: self.comparator('gt', a),
            JLE: lambda a, b: self.comparator('le', a),
            JLT: lambda a, b: self.comparator('lt', a),
            # ---Memory write/read
            LD: lambda a, b: self.ld(a, b),
            ST: lambda a, b: self.st(a, b),
            # ---Print character
            PRA: lambda a, b: print(chr(self.reg[a]))
        }
        self.PC = 0
        self.FL = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.IM = 5
        self.IS = 6
        self.SP = 7
        self.KEY = 0xF4
        self.reg[self.SP] = 0xF4
        self.timer = 0
        self.interrupts_allowed = True

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
        inter_vectors = {
            0: 0xF8,
            1: 0xF9,
            2: 0xFA,
            3: 0xFB,
            4: 0xFC,
            5: 0xFD,
            6: 0xFE,
            7: 0xFF
        }
        masked_interrupts = self.reg[self.IM] & self.reg[self.IS]
        for i in range(8):
            interrupt_happened = ((masked_interrupts >> i) & 1) == 1
            if interrupt_happened:
                self.interrupt_prep()
                # move PC for cpu.run to go to interrupt handler
                self.PC = self.ram_read(inter_vectors[i])
                break;

    def interrupt_prep(self):
        '''Preps cpu to handle the interruption by storing data'''
        self.interrupts_allowed = False
        self.reg[self.IS] = 0
        # store PC
        self.reg[self.SP] -= 1
        self.ram_write(self.reg[self.SP], self.PC)
        # store FL
        self.reg[self.SP] -= 1
        self.ram_write(self.reg[self.SP], self.FL)
        # store registers 0-6
        for i in range(7):
            self.push_stack(i)

    def interrupt(self, interrupt):
        '''Manually trigge an interruption from within cpu.run'''
        value = 0b1 << interrupt
        self.reg[self.IS] = value

    def inter_ret(self):
        '''IRET occurs. Restore previously saved data'''
        for i in range(6, -1, -1):
            self.pop_stack(i)
        self.FL = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1
        self.PC = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1
        self.interrupts_allowed = True
        self.timer = datetime.now()

    def run(self):
        """Run the CPU."""
        halted = False
        self.timer = datetime.now()

        while not halted:
            # see if currently handling another interruption
            if self.interrupts_allowed:
                new_time = datetime.now()
                # check for timer interrupt
                if (new_time - self.timer).seconds >= 3:
                    self.timer = new_time
                    self.interrupt(0)
                key_pressed = msvcrt.kbhit()
                # check for keyboard interrupt
                if key_pressed:
                    key = msvcrt.getch().decode()
                    code = ord(key)
                    self.ram_write(self.KEY, code)
                    self.interrupt(1)
                # check IS register for interrupts
                self.check_interrupts()

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
