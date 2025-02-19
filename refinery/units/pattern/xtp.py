#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from fnmatch import fnmatch
from ipaddress import ip_address
from typing import AnyStr
from urllib.parse import urlparse
from string import ascii_letters
from pathlib import Path
from enum import Enum

from refinery.units.pattern import arg, PatternExtractor
from refinery.units import RefineryCriticalException
from refinery.lib.patterns import indicators


class LetterWeight:
    def __init__(self, weight):
        try:
            self._weights = weight._weights
        except AttributeError:
            pass
        else:
            return
        self._weights = {
            letter: weight for letters, weight in weight.items() for letter in letters
        }
        for letter in range(0x100):
            self._weights.setdefault(letter, 0)

    def __call__(self, data: AnyStr) -> float:
        if isinstance(data, str):
            data = data.encode('latin1')
        return sum(self._weights[c] for c in data) / len(data) / max(self._weights.values())


class LetterWeights(LetterWeight, Enum):
    IOC = LetterWeight({
        B'^`': 1,
        B'!$%&()*+-<=>?[]{}~\t': 2,
        B'ABCDEFGHIJKLMNOPQRSTUVWXYZ': 4,
        B'.,:;#/\\|@_ ': 5,
        B'0123456789abcdefghijklmnopqrstuvwxyz': 8,
    })
    Path = LetterWeight({
        B'^`': 1,
        B'$%&()*+-<=>?[]{}~\t': 2,
        B'.,:;#/\\|@_ ': 4,
        B'0123456789': 4,
        B'ABCDEFGHIJKLMNOPQRSTUVWXYZ': 5,
        B'abcdefghijklmnopqrstuvwxyz': 8,
    })


class xtp(PatternExtractor):
    """
    Extract Patterns: Uses regular expressions to extract indicators from the input data and
    optionally filters these results heuristically. The unit is designed to extract indicators
    such as domain names and IP addresses, see below for a complete list. To extract data
    formats such as hex-encoded data, use `refinery.carve`.
    """

    def __init__(
        self,
        *pattern: arg('pattern', type=str,
            default=(
                indicators.hostname.name,
                indicators.url.name,
                indicators.email.name,
            ), help=(
                'Choose the pattern to extract. The unit uses {{default}} by default. Use an '
                'asterix character to select all available patterns. The available patterns '
                'are: {}'.format(', '.join(p.dashname for p in indicators))
            )
        ),
        filter: arg('-f', dest='filter', action='count',
            help=(
                'If this setting is enabled, the xtp unit will attempt to reduce the number '
                'of false positives by certain crude heuristics. Specify multiple times to '
                'make the filtering more aggressive.'
            )
        ) = 0,
        min=1, max=None, len=None, stripspace=False, duplicates=False, longest=False, take=None
    ):
        self.superinit(super(), **vars(), ascii=True, utf16=True)

        patterns = {
            p for name in pattern for p in indicators if fnmatch(p.dashname, name)
        }
        # if indicators.hostname in patterns:
        #     patterns.remove(indicators.hostname)
        #     patterns.add(indicators.ipv4)
        #     patterns.add(indicators.domain)
        patterns = [F'(?P<{p.name}>{p.value})' for p in patterns]
        if not patterns:
            raise RefineryCriticalException('The given mask does not match any known indicator pattern.')
        pattern = '|'.join(patterns)
        self.args.pattern = re.compile(pattern.encode(self.codec), flags=re.DOTALL)
        self.args.filter = filter

    _ALPHABETIC = ascii_letters.encode('ASCII')
    _LEGITIMATE_HOSTS = {
        'acm.org'                 : 1,
        'adobe.com'               : 1,
        'aka.ms'                  : 1,
        'android.com'             : 1,
        'apache.org'              : 1,
        'apple.com'               : 1,
        'archive.org'             : 2,
        'azure.com'               : 1,
        'baidu.com'               : 2,
        'comodo.net'              : 1,
        'comodoca.com'            : 1,
        'curl.haxx.se'            : 1,
        'digicert.com'            : 1,
        'dublincore.org'          : 1,
        'github.com'              : 3,
        'globalsign.com'          : 1,
        'globalsign.net'          : 1,
        'godaddy.com'             : 1,
        'google.com'              : 4,
        'gov'                     : 2,
        'iana.org'                : 1,
        'intel.com'               : 1,
        'live.com'                : 1,
        'microsoft.com'           : 1,
        'msdn.com'                : 1,
        'msn.com'                 : 1,
        'office.com'              : 1,
        'openssl.org'             : 1,
        'openxmlformats.org'      : 1,
        'purl.org'                : 1,
        'python.org'              : 1,
        'sectigo.com'             : 1,
        'skype.com'               : 1,
        'sourceforge.net'         : 4,
        'sway-cdn.com'            : 1,
        'sway-extensions.com'     : 1,
        'symantec.com'            : 1,
        'symauth.com'             : 1,
        'symcb.com'               : 1,
        'symcd.com'               : 1,
        'thawte.com'              : 1,
        'usertrust.com'           : 1,
        'verisign.com'            : 1,
        'w3.org'                  : 1,
        'wikipedia.org'           : 1,
        'wolfram.com'             : 1,
        'xml.org'                 : 1,
        'xmlsoap.org'             : 1,
        'yahoo.com'               : 1,
        'googleapis.com'          : 1,
        'fontawesome.com'         : 1,
        'jquery.com'              : 1,
        'cdnjs.cloudflare.com'    : 4,
        'bootstrapcdn.com'        : 2,
        'jsdelivr.net'            : 2,
        'office365.com'           : 2,
    }

    _DOMAIN_WHITELIST = [
        'system.net',
        'wscript.shell',
    ]

    _BRACKETING = {
        B"'"[0]: B"'",
        B'"'[0]: B'"',
        B'('[0]: B')',
        B'{'[0]: B'}',
        B'['[0]: B']',
        B'<'[0]: B'>',
    }

    def _check_match(self, data, pos, name, value):
        term = self._BRACKETING.get(data[pos - 1], None)
        if term:
            pos = value.find(term)
            if pos > 0:
                value = value[:pos]
        if not self.args.filter:
            return value
        if name == indicators.ipv4.name:
            ocets = [int(x) for x in value.split(B'.')]
            if ocets.count(0) >= 3:
                return None
            for area in (
                data[pos - 20 : pos + 20],
                data[pos * 2 - 40 : pos * 2 + 40 : 2],
                data[pos * 2 - 41 : pos * 2 + 39 : 2]
            ):
                if B'version' in area.lower():
                    return None
            ip = ip_address(value.decode(self.codec))
            if not ip.is_global:
                if self.args.filter >= 3 or not ip.is_private:
                    return None
        elif name in {
            indicators.url.name,
            indicators.socket.name,
            indicators.hostname.name,
            indicators.domain.name,
            indicators.subdomain.name
        }:
            if self.args.filter >= 2:
                if LetterWeights.IOC(value) < 0.6:
                    return None
                if name != indicators.url.name and len(value) > 0x100:
                    return None
            ioc = value.decode(self.codec)
            if '://' not in ioc: ioc = F'tcp://{ioc}'
            parts = urlparse(ioc)
            host, _, _ = parts.netloc.partition(':')
            hl = host.lower()
            for white, level in self._LEGITIMATE_HOSTS.items():
                if self.args.filter >= level and hl == white or hl.endswith(F'.{white}'):
                    return None
            if name == indicators.url.name:
                scheme = parts.scheme.lower()
                for p in ('http', 'https', 'ftp', 'file', 'mailto'):
                    if scheme.endswith(p):
                        pos = scheme.find(p)
                        value = value[pos:]
                        break
            if any(hl == w for w in self._DOMAIN_WHITELIST):
                return None
            if name in {
                indicators.hostname.name,
                indicators.domain.name,
                indicators.subdomain.name
            }:
                hostparts = host.split('.')
                if self.args.filter >= 2:
                    # remove hostnames where no part is longer than three characters.
                    if all(len(p) < 4 for p in hostparts):
                        return None
                if self.args.filter >= 3:
                    # remove hostnames where more than one third of the parts are mixed case.
                    if len(hostparts) <= sum(3 for p in hostparts if p != p.lower() and p != p.upper()):
                        return None
                # These heuristics attempt to filter out member access to variables in
                # scripts which can be mistaken for domains because of the TLD inflation
                # we've had.
                uppercase = sum(1 for c in host if c.isalpha() and c.upper() == c)
                lowercase = sum(1 for c in host if c.isalpha() and c.lower() == c)
                if lowercase and uppercase:
                    caseratio = uppercase / lowercase
                    if 0.1 < caseratio < 0.9:
                        return None
                if all(x.isidentifier() for x in hostparts):
                    if len(hostparts) == 2 and hostparts[0] == 'this':
                        return None
                    if len(hostparts[-2]) < 3:
                        return None
                    if any(x.startswith('_') for x in hostparts):
                        return None
                    if len(hostparts[-1]) > 3:
                        seen_before = len(set(re.findall(
                            R'{}(?:\.\w+)+'.format(hostparts[0]).encode('ascii'), data)))
                        if seen_before > 2:
                            return None
        elif name == indicators.email.name:
            at = value.find(B'@')
            ix = 0
            while value[ix] not in self._ALPHABETIC:
                ix += 1
            return None if at - ix < 3 else value[ix:]
        elif name == indicators.path.name:
            try:
                path = value.decode(self.codec)
            except Exception:
                return None
            try:
                path = Path(path)
            except Exception as E:
                self.log_debug(F'error parsing path "{path}": {E!s}')
                return None
            for k, part in enumerate(path.parts):
                if not k:
                    if part.endswith(':') and len(part) == 2:
                        continue
                    if part[0] == part[~0] == '%':
                        continue
                if LetterWeights.Path(part) < 0.6:
                    return None
            if len(value) < 8:
                return None
            if len(value) > 16 and len(re.findall(RB'\\x\d\d', value)) > len(value) // 10:
                return None
        return value

    def process(self, data):
        whitelist = set()

        def check(match):
            for name, value in match.groupdict().items():
                if value is not None:
                    break
            else:
                raise RefineryCriticalException('Received empty match.')
            if value in whitelist:
                return None
            result = self._check_match(data, match.start(), name, value)
            if result is not None:
                return self.labelled(result, pattern=name)
            whitelist.add(value)

        self.log_debug(self.args.pattern.pattern)

        transforms = [check]
        yield from self.matches_filtered(memoryview(data), self.args.pattern, *transforms)
