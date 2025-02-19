#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from refinery import b64, b85, map
from .. import TestUnitBase


class TestBaseUnit(TestUnitBase):

    def test_inversion_base_02e(self):
        unit = self.load('-e', '2')
        data = self.generate_random_buffer(24)
        self.assertEqual(data, unit.process(unit.reverse(data)))

    def test_inversion_base_02E(self):
        unit = self.load('2')
        data = self.generate_random_buffer(24)
        self.assertEqual(data, unit.process(unit.reverse(data)))

    def test_inversion_base_10(self):
        unit = self.load('10')
        data = self.generate_random_buffer(24)
        self.assertEqual(data, unit.process(unit.reverse(data)))

    def test_inversion_base_16re(self):
        unit = self.load()
        data = B'0xBAADF00DC0FFEEBABE'
        self.assertEqual(data, unit.reverse(unit.process(data)))

    def test_inversion_base_16(self):
        unit = self.load('0x10')
        data = B'BAADF00DC0FFEEBABE'
        self.assertEqual(data, unit.reverse(unit.process(data)))

    def test_invalid_base_values(self):
        self.assertRaises(Exception, self.load, 1)
        self.assertRaises(Exception, self.load, 37)
        self.assertRaises(Exception, self.load, -2)

    def test_hardcoded_example_base_36(self):
        unit = self.load(36)
        data = B'BINARYREFINERY'
        self.assertEqual(data, unit.reverse(unit.process(data)))

    def test_base64_01(self):
        unit = self.load(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/')
        data = self.generate_random_buffer(200)
        self.assertEqual(bytes(data | -self.ldu('b64') | unit), data)

    def test_base64_02(self):
        alphabet = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        shuffled = b'tu1grak3IXc2p/yfY4mqMQbZEOD7Nhl9G06eB+RFCALi8jW5ToKJVwSdPvsUHznx'
        unit = self.load(alphabet=shuffled)
        data = self.generate_random_buffer(200)
        self.assertEqual(bytes(data | -b64 | map(alphabet, shuffled) | unit), data)

    def test_base85_01(self):
        unit = self.load(alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~')
        data = self.generate_random_buffer(200)
        self.assertEqual(bytes(data | -b85 | unit), data)

    def test_base85_02(self):
        alphabet = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~'
        shuffled = b'HD+>Wg&c;Rp}_N!a|1i#5IC<mG=(wOlZ2~?8`s*PXyToSveQ@$96Lru%t7zUkq{3BYA40M)E-jdKJhbxVfF^n'
        unit = self.load(alphabet=shuffled)
        data = self.generate_random_buffer(200)
        self.assertEqual(bytes(data | -b85 | map(alphabet, shuffled) | unit), data)
