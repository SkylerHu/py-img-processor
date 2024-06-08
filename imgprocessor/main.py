#!/usr/bin/env python
# coding=utf-8
import typing
import sys
import argparse

from imgprocessor import VERSION


def main(argv: typing.Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog='pre-commit')

    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'%(prog)s {VERSION}',
    )
    if len(argv) == 0:
        argv = ['run']
    args = parser.parse_args(argv)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
