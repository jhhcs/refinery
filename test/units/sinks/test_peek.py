#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import contextlib
import inspect
import io
import sys

from .. import TestUnitBase

from refinery.lib.frame import Chunk
from refinery.lib.loader import load_pipeline as L
from refinery import drain


@contextlib.contextmanager
def errbuf():
    sys_stderr = sys.stderr
    sys.stderr = io.StringIO()
    yield sys.stderr
    sys.stderr = sys_stderr


def bindoc(cls):
    return inspect.getdoc(cls).encode('utf8')


class TestPeek(TestUnitBase):

    TESTBUFFER_BIN = bytes.fromhex( # start of a notepad.exe
        '4D 5A 90 00 03 00 00 00 04 00 00 00 FF FF 00 00 B8 00 00 00 00 00 00 00'
        '40 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
        '00 00 00 00 00 00 00 00 00 00 00 00 F8 00 00 00 0E 1F BA 0E 00 B4 09 CD'
        '21 B8 01 4C CD 21 54 68 69 73 20 70 72 6F 67 72 61 6D 20 63 61 6E 6E 6F'
        '74 20 62 65 20 72 75 6E 20 69 6E 20 44 4F 53 20 6D 6F 64 65 2E 0D 0D 0A'
        '24 00 00 00 00 00 00 00 65 39 D7 74 21 58 B9 27 21 58 B9 27 21 58 B9 27'
        '28 20 2A 27 11 58 B9 27 35 33 BD 26 2B 58 B9 27 35 33 BA 26 22 58 B9 27'
        '35 33 B8 26 28 58 B9 27 21 58 B8 27 0B 5D B9 27 35 33 B1 26 3F 58 B9 27'
        '35 33 BC 26 3E 58 B9 27 35 33 44 27 20 58 B9 27 35 33 46 27 20 58 B9 27'
        '35 33 BB 26 20 58 B9 27 52 69 63 68 21 58 B9 27 00 00 00 00 00 00 00 00'
        '00 00 00 00 00 00 00 00 50 45 00 00 64 86 07 00 18 36 A6 3B 00 00 00 00'
        '00 00 00 00 F0 00 22 00 0B 02 0E 14 00 5E 02 00 00 E6 00 00 00 00 00 00'
        '10 54 02 00 00 10 00 00 00 00 00 40 01 00 00 00 00 10 00 00 00 02 00 00'
        '0A 00 00 00 0A 00 00 00 0A 00 00 00 00 00 00 00 00 90 03 00 00 04 00 00'
        'D3 F1 03 00 02 00 60 C1 00 00 08 00 00 00 00 00 00 10 01 00 00 00 00 00'
        '00 00 10 00 00 00 00 00 00 10 00 00 00 00 00 00 00 00 00 00 10 00 00 00'
        '00 00 00 00 00 00 00 00 D8 E6 02 00 44 02 00 00 00 70 03 00 D8 0B 00 00'
        '00 40 03 00 88 11 00 00 00 00 00 00 00 00 00 00 00 80 03 00 E8 02 00 00'
        'A0 BC 02 00 54 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
        '00 00 00 00 00 00 00 00 10 77 02 00 18 01 00 00 00 00 00 00 00 00 00 00'
        '28 78 02 00 10 09 00 00 F0 DF 02 00 E0 00 00 00 00 00 00 00 00 00 00 00'
        '00 00 00 00 00 00 00 00 2E 74 65 78 74 00 00 00 CF 5C 02 00 00 10 00 00'
        '00 5E 02 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 20 00 00 60'
        '2E 72 64 61 74 61 00 00 D6 98 00 00 00 70 02 00 00 9A 00 00 00 62 02 00'
        '00 00 00 00 00 00 00 00 00 00 00 00 40 00 00 40 2E 64 61 74 61 00 00 00'
        '88 27 00 00 00 10 03 00 00 0E 00 00 00 FC 02 00 00 00 00 00 00 00 00 00'
        '00 00 00 00 40 00 00 C0 2E 70 64 61 74 61 00 00 88 11 00 00 00 40 03 00'
        '00 12 00 00 00 0A 03 00 00 00 00 00 00 00 00 00 00 00 00 00 40 00 00 40'
        '2E 64 69 64 61 74 00 00 78 01 00 00 00 60 03 00 00 02 00 00 00 1C 03 00'
        '00 00 00 00 00 00 00 00 00 00 00 00 40 00 00 C0 2E 72 73 72 63 00 00 00'
    )

    TESTBUFFER_TXT = inspect.cleandoc(
        """
            Another one got caught today, it's all over the papers.  "Teenager
        Arrested in Computer Crime Scandal", "Hacker Arrested after Bank Tampering"...
            Damn kids.  They're all alike.

            But did you, in your three-piece psychology and 1950's technobrain,
        ever take a look behind the eyes of the hacker?  Did you ever wonder what
        made him tick, what forces shaped him, what may have molded him?
            I am a hacker, enter my world...
            Mine is a world that begins with school... I'm smarter than most of
        the other kids, this crap they teach us bores me...
            Damn underachiever.  They're all alike.

            I'm in junior high or high school.  I've listened to teachers explain
        for the fifteenth time how to reduce a fraction.  I understand it.  "No, Ms.
        Smith, I didn't show my work.  I did it in my head..."
            Damn kid.  Probably copied it.  They're all alike.
        """
    ).encode('utf8')

    def test_hex_peek(self):
        peek = self.load(width=8, lines=15)
        with errbuf() as stderr:
            peek(bytes.fromhex(
                '4D 5A 90 00 03 00 00 00 04 00 00 00 FF FF 00 00'  # MZ..............
                'B8 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00'  # ........@.......
                '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'  # ................
                '00 00 00 00 00 00 00 00 00 00 00 00 F8 00 00 00'  # ................
                '0E 1F BA 0E 00 B4 09 CD 21 B8 01 4C CD 21 54 68'  # ........!..L.!Th
                '69 73 20 70 72 6F 67 72 61 6D 20 63 61 6E 6E 6F'  # is.program.canno
                '74 20 62 65 20 72 75 6E 20 69 6E 20 44 4F 53 20'  # t.be.run.in.DOS.
                '6D 6F 64 65 2E 0D 0D 0A 24 00 00 00 00 00 00 00'  # mode....$.......
            ))
            output = stderr.getvalue()

        self.assertIn('45.87% entropy', output)

        self.assertIn((
            '-------------------------------------\n'
            '00: 4D 5A 90 00 03 00 00 00  MZ......\n'
            '08: 04 00 00 00 FF FF 00 00  ........\n'
            '10: B8 00 00 00 00 00 00 00  ........\n'
            '18: 40 00 00 00 00 00 00 00  @.......\n'
            '20: 00 00 00 00 00 00 00 00  ........\n'
            '..: === repeats 2 times ===  ========\n'
            '38: 00 00 00 00 F8 00 00 00  ........\n'
            '40: 0E 1F BA 0E 00 B4 09 CD  ........\n'
            '48: 21 B8 01 4C CD 21 54 68  !..L.!Th\n'
            '50: 69 73 20 70 72 6F 67 72  is.progr\n'
            '58: 61 6D 20 63 61 6E 6E 6F  am.canno\n'
            '60: 74 20 62 65 20 72 75 6E  t.be.run\n'
            '68: 20 69 6E 20 44 4F 53 20  .in.DOS.\n'
            '70: 6D 6F 64 65 2E 0D 0D 0A  mode....\n'),
            output
        )

    def test_regression_all_output(self):
        data = b'Refining Binaries since 2019'
        peek = self.load(all=True, decode=True)
        with errbuf() as stderr:
            peek(data)
            test = stderr.getvalue()
        self.assertIn(data.decode('ascii'), test)

    def test_binary_NB1(self):
        desired = inspect.cleandoc(
            """
            -----------------------------------------------------------------
            4D 5A 90 00 03 00 00 00 04 00 00 00 FF FF 00 00  MZ..............
            B8 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00  ........@.......
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
            00 00 00 00 00 00 00 00 00 00 00 00 F8 00 00 00  ................
            0E 1F BA 0E 00 B4 09 CD 21 B8 01 4C CD 21 54 68  ........!..L.!Th
            69 73 20 70 72 6F 67 72 61 6D 20 63 61 6E 6E 6F  is.program.canno
            74 20 62 65 20 72 75 6E 20 69 6E 20 44 4F 53 20  t.be.run.in.DOS.
            6D 6F 64 65 2E 0D 0D 0A 24 00 00 00 00 00 00 00  mode....$.......
            65 39 D7 74 21 58 B9 27 21 58 B9 27 21 58 B9 27  e9.t!X.'!X.'!X.'
            28 20 2A 27 11 58 B9 27 35 33 BD 26 2B 58 B9 27  (.*'.X.'53.&+X.'
            -----------------------------------------------------------------
            """
        )
        peek = self.load(bare=True, narrow=True, width=16)
        with errbuf() as stderr:
            peek(self.TESTBUFFER_BIN)
            out = stderr.getvalue().strip()
        self.assertEqual(out, desired)

    def test_binary_NB2(self):
        desired = inspect.cleandoc(
            """
            ---------------------------------------------------------
            4D5A 9000 0300 0000 0400 0000 FFFF 0000  MZ..............
            B800 0000 0000 0000 4000 0000 0000 0000  ........@.......
            0000 0000 0000 0000 0000 0000 0000 0000  ................
            0000 0000 0000 0000 0000 0000 F800 0000  ................
            0E1F BA0E 00B4 09CD 21B8 014C CD21 5468  ........!..L.!Th
            6973 2070 726F 6772 616D 2063 616E 6E6F  is.program.canno
            7420 6265 2072 756E 2069 6E20 444F 5320  t.be.run.in.DOS.
            6D6F 6465 2E0D 0D0A 2400 0000 0000 0000  mode....$.......
            6539 D774 2158 B927 2158 B927 2158 B927  e9.t!X.'!X.'!X.'
            2820 2A27 1158 B927 3533 BD26 2B58 B927  (.*'.X.'53.&+X.'
            ---------------------------------------------------------
            """
        )
        peek = self.load(bare=True, narrow=True, width=8, blocks=2)
        with errbuf() as stderr:
            peek(self.TESTBUFFER_BIN)
            out = stderr.getvalue().strip()
        self.assertEqual(out, desired)

    def test_binary_B4(self):
        desired = inspect.cleandoc(
            """
            ----------------------------------------------------------
            000: 4D5A9000 03000000 04000000 FFFF0000  MZ..............
            004: B8000000 00000000 40000000 00000000  ........@.......
            008: 00000000 00000000 00000000 00000000  ................
            00C: 00000000 00000000 00000000 F8000000  ................
            010: 0E1FBA0E 00B409CD 21B8014C CD215468  ........!..L.!Th
            014: 69732070 726F6772 616D2063 616E6E6F  is.program.canno
            018: 74206265 2072756E 20696E20 444F5320  t.be.run.in.DOS.
            01C: 6D6F6465 2E0D0D0A 24000000 00000000  mode....$.......
            020: 6539D774 2158B927 2158B927 2158B927  e9.t!X.'!X.'!X.'
            024: 28202A27 1158B927 3533BD26 2B58B927  (.*'.X.'53.&+X.'
            ----------------------------------------------------------
            """
        )
        peek = self.load(bare=True, narrow=False, width=4, blocks=4)
        with errbuf() as stderr:
            peek(self.TESTBUFFER_BIN)
            out = stderr.getvalue().strip()
        self.assertEqual(out, desired)

    def test_printable_decoded(self):
        desired = inspect.cleandoc(
            """
            --CODEC=UTF8--------------------------------------------------------------------
                Another one got caught today, it's all over the papers.  "Teenager
            Arrested in Computer Crime Scandal", "Hacker Arrested after Bank Tampering"...
                Damn kids.  They're all alike.
                But did you, in your three-piece psychology and 1950's technobrain,
            ever take a look behind the eyes of the hacker?  Did you ever wonder what
            made him tick, what forces shaped him, what may have molded him?
                I am a hacker, enter my world...
                Mine is a world that begins with school... I'm smarter than most of
            the other kids, this crap they teach us bores me...
                Damn underachiever.  They're all alike.
            --------------------------------------------------------------------------------
            """
        )
        peek = self.load(bare=True, decode=True, width=80)
        with errbuf() as stderr:
            peek(self.TESTBUFFER_TXT)
            out = stderr.getvalue().strip()
        self.assertEqual(out, desired)

    def test_printable_escaped(self):
        desired = inspect.cleandoc(
            R"""
            ------------------------------------------------------------------------
                Another one got caught today, it's all over the papers.  "Teenager\n
            Arrested in Computer Crime Scandal", "Hacker Arrested after Bank Tamperi
            ng"...\n    Damn kids.  They're all alike.\n\n    But did you, in your t
            hree-piece psychology and 1950's technobrain,\never take a look behind t
            he eyes of the hacker?  Did you ever wonder what\nmade him tick, what fo
            rces shaped him, what may have molded him?\n    I am a hacker, enter my 
            world...\n    Mine is a world that begins with school... I'm smarter tha
            n most of\nthe other kids, this crap they teach us bores me...\n    Damn
             underachiever.  They're all alike.\n\n    I'm in junior high or high sc
            hool.  I've listened to teachers explain\nfor the fifteenth time how to 
            ------------------------------------------------------------------------
            """
        )
        peek = self.load(bare=True, escape=True, width=72)
        with errbuf() as stderr:
            peek(self.TESTBUFFER_TXT)
            out = stderr.getvalue().strip()
        self.assertEqual(out, desired)

    def test_gzip_from_libmagic(self):
        data = self.download_sample('2bda560f264fb4eea5e180f32913197ec441ed8d6852a5cbdb6763de7bbf4ecf')
        peek = self.load(width=70)
        with errbuf() as stderr:
            peek(data)
            out = stderr.getvalue().strip()
        self.assertIn('1F 8B 08 00 00 00 00 00 04 00', out)

    def test_encoding_metavars(self):
        pfmt = 'emit s: [| put test "s:{}" | peek ]'
        for value, requires_prefix in {
            'b64:b64:b64' : True,
            'accu:$msvc'  : True,
            'u[:!krz--dk' : False,
            'ftp://t.com' : False,
        }.items():
            with errbuf() as stderr:
                prefix = 's:' * requires_prefix
                L(pfmt.format(value))()
                self.assertIn(F'test = {prefix}{value}', stderr.getvalue())
