#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()
options = {'call', 'interrupts', 'keyboard', 'mult', 'print8', 'printstr',
           'sctest', 'stack', 'stackoverflow'}
try:
    program = sys.argv[1]
    if program in options:
        cpu.load(program)
        cpu.run()
    else:
        print('LS-8 does not know that program yet.')
except IndexError:
    print("You need to input a file name.")
