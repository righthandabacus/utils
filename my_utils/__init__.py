# -*- coding: utf-8 -*-

"""Generic and reusable functions"""

__version__ = '0.0.4'
__author__ = 'Adrian Tam'
__date__ = "2019-09-21"
__author_email__ = 'adrian.sw.tam@gmail.com'

from .feeds import add_feed_data_ver, get_feed_data, is_feed, is_base_feed, \
        list_feed_data_vers, list_feed_subfeeds, list_feed_vers, list_feeds
from .utils import exception_hook, print_tb_with_local, supports_color, \
        get_logger, readxml, readkeyval, readyaml, email, curl, sieve, flatten, \
        subdict
from .iters import take, prepend, tabulate, tail, consume, nth, all_equal, \
        quantify, padnone, ncycles, dotproduct, flatten, repeatfunc, pairwise, \
        grouper, roundrobin, partition, powerset, unique_everseen, \
        unique_justseen, iter_except, first_true, random_product, \
        random_permutation, random_combination, \
        random_combination_with_replacement, nth_combination
from .unicode import unicoderemove, unicodereplace, \
        deaccent, depunctuation, \
        letters_only, digits_only, letters_tokens
from .excel import pixel2colwidth, str2pixels
try:
    from .web.browser import browser
except ImportError:
    pass  # ignore if no selenium

# vim:set ts=4 sw=4 sts=4 tw=100 fdm=indent et:
