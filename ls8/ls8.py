#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()
program = sys.argv[1] if len(sys.argv) > 1 else 'no input'
options = set(['call', 'interrupts', 'keyboard', 'mult', 'print8', 'printstr',
              'sctest', 'stack', 'stackoverflow'])
if program in options:
    cpu.load(program)
    cpu.run()
else:
    print(f"LS-8 can't run {program} yet!")
    sys.exit(1)