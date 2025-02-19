#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from http.client import HTTPResponse

from refinery import Unit
from refinery.lib.structures import MemoryFile


class SockWrapper(MemoryFile):
    def sendall(self, ___): pass
    def makefile(self, *_): return self


class httpresponse(Unit):
    """
    Parses HTTP response text, as you would obtain from a packet dump. This can be
    useful if chunked or compressed transfer encoding was used.
    """
    def process(self, data):
        with SockWrapper(data) as mock:
            mock.seek(0)
            parser = HTTPResponse(mock)
            parser.begin()
            return parser.read()
