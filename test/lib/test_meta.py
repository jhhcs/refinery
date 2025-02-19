#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from refinery.lib.meta import metavars
from refinery.lib.frame import Chunk
from refinery.lib.loader import load_pipeline

from .. import TestBase


class TestMeta(TestBase):

    def test_binary_printer_for_integer_arrays(self):
        data = Chunk()
        data['k'] = [t for t in b'refinery']
        meta = metavars(data)
        self.assertEqual(meta.format_bin('{k:itob}', 'utf8', data), b'refinery')

    def test_binary_formatter_fallback(self):
        data = self.generate_random_buffer(3210)
        meta = metavars(data)
        self.assertEqual(meta.format_bin('{size!r}', 'utf8', data).strip(), b'3.210 kB')

    def test_binary_formatter_literal(self):
        meta = metavars(B'')
        self.assertEqual(meta.format_bin('{726566696E657279!H}', 'utf8'), b'refinery')
        self.assertEqual(meta.format_bin('{refinery!a}', 'utf8'), 'refinery'.encode('latin1'))
        self.assertEqual(meta.format_bin('{refinery!s}', 'utf8'), 'refinery'.encode('utf8'))
        self.assertEqual(meta.format_bin('{refinery!u}', 'utf8'), 'refinery'.encode('utf-16le'))

    def test_hex_byte_strings(self):
        pl = load_pipeline('emit Hello [| cm -2 | cfmt {sha256!r} ]')
        self.assertEqual(pl(), b'185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969')
