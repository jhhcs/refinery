#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from typing import Iterable

from refinery.units.blockwise import arg, BlockTransformationBase
from refinery.units.encoding.base import base as BaseUnit
from refinery.lib.argformats import number
from refinery.lib.patterns import formats


class pack(BlockTransformationBase):
    """
    Scans the input data for numeric constants and packs them into a binary
    format. This is useful to convert the textual representation of an array of
    numbers into its binary form. For example, `123,34,256,12,1,234` would be
    transformed into the byte sequence `7B22000C01EA`, where `256` was wrapped
    and packed as a null byte because the default block size is one byte. If
    the above sequence would be packed with options -EB2, the result would be
    equal to `007B00220100000C000100EA` in hexadecimal.
    """

    def __init__(self,
        base: arg(type=number[2:36], help=(
            'Find only numbers in given base. Default of 0 means that '
            'common expressions for hexadecimal, octal and binary are '
            'accepted.')) = 0,
        prefix  : arg.switch('-r', help='Add numeric prefixes like 0x, 0b, and 0o in reverse mode.') = False,
        strict  : arg.switch('-s', help='Only parse integers that fit in one block of the given block size.') = False,
        bigendian=False, blocksize=1
    ):
        super().__init__(
            base=base,
            prefix=prefix,
            strict=strict,
            bigendian=bigendian,
            blocksize=blocksize
        )

    @property
    def bytestream(self):
        # never alow bytes to be left unchunked
        return False

    def reverse(self, data):
        base = self.args.base or 10
        prefix = B''

        self.log_debug(F'using base {base:d}')

        if self.args.prefix:
            prefix = {
                0x02: b'0b',
                0x08: b'0o',
                0x10: b'0x'
            }.get(base, B'')

        converter = BaseUnit(base, not self.args.bigendian)

        for n in self.chunk(data, raw=True):
            yield prefix + converter.reverse(n)

    def process(self, data):
        base: int = self.args.base
        strict: bool = self.args.strict

        def intb(literals: Iterable[bytes]):
            for literal in literals:
                if base == 0 and literal[0] == 0x30 and literal[1:].isdigit():
                    literal = B'0o%s' % literal
                N = int(literal, base)
                M = N & self.fmask
                if strict and M != N:
                    continue
                yield M

        if base == 0:
            pattern = formats.integer
        elif base <= 10:
            pattern = re.compile(B'[-+]?[0-%d]{1,64}' % (base - 1))
        else:
            pattern = re.compile(B'[-+]?[0-9a-%c]{1,20}' % (0x57 + base), re.IGNORECASE)

        it = (m[0] for m in pattern.finditer(data))
        return self.unchunk(intb(it))
