#!/usr/bin/env python3
"""Inspect smali file.

Usage:
    inspect.py -i File.smali [-e] [-m]

Options:
    -h --help      Show this screen.
    -i <filename>  Input filename to inspect.
    -e             Inspect Exceptions
    -m             Inspect Methods
"""

from docopt import docopt
import smali.source
import smali.parser
import smali.emulator


def main(arguments):
    """Main method."""
    filename = arguments.get('-i')
    if arguments.get('-e'):
        inspect_exceptions(filename)
    if arguments.get('-m'):
        inspect_methods(filename)


def inspect_exceptions(filename):
    """Inspect exceptions in the smali file."""
    emu = smali.emulator.Emulator(
        source=smali.source.get_source_from_file(filename)
    )
    emu.preproc_source()
    print(emu.vm.catch_blocks)


def inspect_methods(filename):
    """Inspect methods in the smali file."""
    methods = smali.parser.extract_methods(
        smali.source.get_source_from_file(filename)
    )
    for method in sorted(methods.keys()):
        print(method)


if __name__ == '__main__':
    main(docopt(__doc__))

