#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .. import TestUnitBase


class TestALU(TestUnitBase):

    def test_index_starts_at_zero(self):
        unit = self.load("B+I")
        self.assertEqual(bytes(bytes(5) | unit), bytes(range(5)))

    def test_real_world_01(self):
        data = bytes.fromhex('7C737376545F0808244368244668652724684643275F2424054B')
        goal = b'https'b'://45.41.204'b'.150:443\0'
        unit = self.load('(41*(B-75))%127')
        self.assertEqual(data | unit | bytes, goal)


class TestALUAgainstOtherUnits(TestUnitBase):

    def setUp(self):
        super().setUp()
        self.buffer = self.generate_random_buffer(1024)
        self.arg = 'BAADF00D'

    def test_against_add(self):
        bop = self.load('B + A', self.arg)
        add = self.ldu('add', self.arg)
        self.assertEqual(add(self.buffer), bop(self.buffer))

    def test_against_sub(self):
        sub = self.ldu('sub', self.arg)
        bop = self.load('B - A', self.arg)
        self.assertEqual(sub(self.buffer), bop(self.buffer))

    def test_against_xor_01(self):
        xor = self.ldu('xor', self.arg)
        bop = self.load('B ^ A', self.arg)
        self.assertEqual(xor(self.buffer), bop(self.buffer))

    def test_against_xor_02(self):
        xor = self.ldu('xor', self.arg)
        bop = self.load('(~B & A) | (B & ~A)', self.arg)
        self.assertEqual(xor(self.buffer), bop(self.buffer))

    def test_against_xor_03(self):
        xor = self.ldu('xor', self.arg)
        bop = self.load('(A | B) & ~(B & A)', self.arg)
        self.assertEqual(xor(self.buffer), bop(self.buffer))

    def test_against_shl(self):
        shl = self.ldu('shl', '3')
        bop = self.load('B << 3')
        self.assertEqual(shl(self.buffer), bop(self.buffer))

    def test_against_shr(self):
        shr = self.ldu('shr', '3')
        bop = self.load('B >> 3')
        self.assertEqual(shr(self.buffer), bop(self.buffer))

    def test_against_ror(self):
        ror = self.ldu('rotr', '3')
        bop = self.load('(B >> 3) | (B << 5)')
        self.assertEqual(ror(self.buffer), bop(self.buffer))
