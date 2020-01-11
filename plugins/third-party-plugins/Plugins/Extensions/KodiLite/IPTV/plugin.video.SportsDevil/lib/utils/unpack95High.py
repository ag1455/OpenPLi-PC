# -*- coding: utf-8 -*-
#
# Unpacker for Dean Edward's p.a.c.k.e.r, a part of javascript beautifier
# by Einar Lielmanis <einar@jsbeautifier.org>
#
#     written by Stefano Sanfilippo <a.little.coder@gmail.com>
#
# usage:
#
# if detect(some_string):
#     unpacked = unpack(some_string)
#

"""Unpacker for Dean Edward's p.a.c.k.e.r"""
import re
import string

class UnpackingError(Exception):
    """Badly packed source or general error. Argument is a
    meaningful description."""
    pass

PRIORITY = 1

def detect(source):
    """Detects whether `source` is P.A.C.K.E.R. coded."""
    return source.replace(' ', '').startswith('eval(function(p,a,c,k,e,r')

def unpack(source):
    """Unpacks P.A.C.K.E.R. packed js code."""
    print len(source)
    payload, symtab, radix, count = _filterargs(source)
    
    modp = r'a\+(\d+)'
    mod = int(re.compile(modp).findall(source)[0])

    if count != len(symtab):
        raise UnpackingError('Malformed p.a.c.k.e.r. symtab.')

    def lookup(match):
        """Look up symbols in the synthetic symtab."""
        word = 0 
        for i, char in enumerate(reversed(match.group(0))):
            word = word + (ord(char)-mod)*(radix**i)
        
        return symtab[word] or word
    
    source = re.sub(ur'[\xa1-\xff]+', lookup, payload)
    return _replacestrings(source)

def _filterargs(source):
    """Juice from a source file the four args needed by decoder."""
    argsregex = (r".*'(.*)'\.split")
    args = re.search(argsregex, source, re.DOTALL).groups()
    ar2 = (r".*?'([\xa1-\xff].*}\);)")
    args2 = re.search(ar2, source, re.DOTALL).groups()
    modp = r'a\+(\d+)'
    mod = int(re.compile(modp).findall(source)[0])
    
    reg = ur'[\xa1-\xff]+'
    ints = re.findall(reg, args2[0], re.DOTALL)
    t = []
    for i in ints:
        t.append(ord(i[-1])-mod)
    
    try:
        return args2[0], args[0].split('|'), max(t)+1, len(args[0].split('|'))
    except ValueError:
        raise UnpackingError('Corrupted p.a.c.k.e.r. data.')

def _replacestrings(source):
    """Strip string lookup table (list) and replace values in source."""
    match = re.search(r'var *(_\w+)\=\["(.*?)"\];', source, re.DOTALL)

    if match:
        varname, strings = match.groups()
        startpoint = len(match.group(0))
        lookup = strings.split('","')
        variable = '%s[%%d]' % varname
        for index, value in enumerate(lookup):
            source = source.replace(variable % index, '"%s"' % value)
        return source[startpoint:]
    return source

