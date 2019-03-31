# -*- coding: utf-8 -*-

__version__ = '0.0.2'
__author__ = 'Adrian Tam'
__date__ = "2019-03-31"
__author_email__ = 'adrian.sw.tam@gmail.com'

from .feeds import add_feed_data_ver, get_feed_data, is_feed, is_base_feed, \
        list_feed_data_vers, list_feed_subfeeds, list_feed_vers, list_feeds
from .utils import curl, email, exception_hook, get_logger, \
        print_tb_with_local, readxml, readyaml, sieve, supports_color
from .iters import take, prepend, tabulate, tail, consume, nth, all_equal, \
        quantify, padnone, ncycles, dotproduct, flatten, repeatfunc, pairwise, \
        grouper, roundrobin, partition, powerset, unique_everseen, \
        unique_justseen, iter_except, first_true, random_product, \
        random_permutation, random_combination, \
        random_combination_with_replacement, nth_combination
from .unicodedata import unicoderemove, unicodereplace, \
        deaccent, depunctuation, \
        lettersOnly, digitsOnly, lettersTokens
from .excel import pixel2colwidth, str2pixels
try:
    from .web.browser import browser
except ImportError:
    pass  # ignore if no selenium

# vim:set ts=4 sw=4 sts=4 tw=100 fdm=indent et:
