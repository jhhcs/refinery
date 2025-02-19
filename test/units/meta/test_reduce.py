#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from refinery.lib.loader import load_pipeline as L
from .. import TestUnitBase


class TestReduce(TestUnitBase):

    def test_concatenation(self):
        pl = L('emit 5 4 3 2 1 0 [| reduce ccp var:t ]')
        self.assertEqual(pl(), B'012345')

    def test_variables_are_retained(self):
        pl = L('emit 5 4 3 2 1 0 [| swap q | reduce --init "" ccp var:q ]')
        self.assertEqual(pl(), B'012345')

    def test_addition(self):
        pl = L('emit 12 20 8 10000 [| pack -B4 | reduce add t | pack -RB4 ]')
        self.assertEqual(pl(), b'10040')
