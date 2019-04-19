#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unicode and string related functions
"""

import unicodedata

def unicoderemove(s, category_check):
    '''
    Remove characters of certain categories from the unicode string

    Args:
        s (str): input string, assumed in utf8 encoding if it is a bytestring
        category_check (callable): a function that takes output of
                unicodedata.category() and returns if such character should be kept in
                the output
    Returns:
        The unicode string of input transformed into normal form KD (compatibility
        decomposition) with characters of the specified categories removed
    '''
    assert isinstance(s, str)
    return "".join(c for c in unicodedata.normalize('NFKD',s) if category_check(unicodedata.category(c)))

def unicodereplace(s, replacer, category_check):
    '''
    Replace characters of certain categories from the unicode string by replacer

    Args:
        s (str): input string, assumed in utf8 encoding if it is a bytestring
        r (str): replacement string
        category_check (callable): a function that takes output of
                unicodedata.category() and returns if such character should be kept in the output
    Returns:
        The unicode string of input transformed into normal form KD (compatibility
        decomposition) with each characters of the specified categories replaced by
        the replacement string
    '''
    if not isinstance(s,unicode):
        s = unicode(s,"utf8")
    return "".join(c if category_check(unicodedata.category(c)) else replacer
                   for c in unicodedata.normalize('NFKD',s))

# Remove characters of nonspacing mark (Mn) category
deaccent = lambda s : unicoderemove(s, lambda c: c!='Mn').replace('\u02b9','')

# Remove punctuations, category names are from http://www.fileformat.info/info/unicode/category/index.htm
depunctuation = lambda s : unicodereplace(s, ' ', lambda c: c not in ['Pc','Pd','Pe','Pf','Pi','Po','Ps'])

# Keep only letters, all CJK ideographs are defined as other letters (Lo)
lettersOnly = lambda s : unicoderemove(s, lambda c: c in ['Ll','Lm','Lo','Lt','Lu'])
digitsOnly = lambda s : unicoderemove(s, lambda c: c == 'Nd')
lettersTokens = lambda s : unicodereplace(s, ' ', lambda c: c in ['Ll','Lm','Lo','Lt','Lu'])


# vim:set ts=4 sw=4 sts=4 tw=100 fdm=indent et:
