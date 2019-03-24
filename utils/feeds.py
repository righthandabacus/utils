# -*- coding: utf-8 -*-

"""Feed utilities.

A feed is a subdirectory under a feed root. And it is in the format like the
following example:

    feedname/0001/versions/20180102235959

The subdirectory name is the name of the feed. Under it there are directories
named after *feed* versions. Feed version is a 4-digit string. A feed will have
version change only if there is substantial format change. For example a
database of XML schema change, or the feed change from CSV format to XML format.
Under the feed version, there must be a directory named "versions".  All files
or directory under "versions" directory shall be a numeric timestamp, as an
identifier of a particular version of *data*.

A particular version of feed data can be:

(1) a single file. In this case the file is having the name of the data version.
With no suffix or extensions. Or,

(2) a directory that contains one or more files. The directory name is the data
version and all files belonged to this version of data goes beneath it. This is
the only way to preserve filename, file extension, or directory hierarchy in a
data version.

All feed data are archived, namely, not supposed to mutate after it is created.
Because of the requirement that version should be numeric, we may create
non-numeric file or directory when we preparing a data version and rename it
after it is finished. When we scan a feed for data versions, all non-numeric
content should therefore skipped to avoid accessing partial data.

This module provides the CRUD operations down to the feed data version level.
"""

import datetime
import os
import shutil
from pipe import where, select, sort, reverse, as_list

__all__ = [
    "list_feeds", "is_feed", "is_base_feed", "list_feed_vers", "list_feed_data_vers",
    "list_feed_subfeeds", "get_feed_data", "add_feed_data_ver"
]

def list_feeds(feedroot):
    """List out names of all feeds

    Args:
        feedroot (str): root dir of the feed repository

    Returns:
        list of strings, each is a valid feed name
    """
    assert os.path.isdir(feedroot)
    names = ( os.listdir(feedroot)
            | where(lambda name: is_feed(os.path.join(feedroot, name)))
            | sort
            | as_list )
    return names

def is_base_feed(dirpath):
    """Check if a directory is a feed directory. It is affirmative if and only
    if (1) it is a directory; (2) contains at least one subdirectory named as a
    4-digit string as the feed version; (3) under the feed version directory
    there is a directory named `versions`; and (4) under `versions` there is
    some all-numeric files or directories

    Args:
        dirpath (str): Directory path to check

    Returns:
        bool for whether a directory looks like a feed directory
    """
    if not os.path.isdir(dirpath):
        return False # not a directory
    ver_dir = ( os.listdir(dirpath)
              | where(lambda name: len(name)==4 and name.isdigit()) # 4-digit
              | select(lambda name: os.path.join(dirpath, name))
              | where(os.path.isdir) # feed ver is a dir
              | select(lambda path: os.path.join(path, 'versions'))
              | where(os.path.isdir) # data ver is a dir
              | where(lambda path: any(name.isdigit() for name in os.listdir(path))) # all-digit
              | as_list ) # list of "feed_name/0001/versions"
    return False if not ver_dir else True

def is_feed(dirpath):
    """Similar to is_base_feed(), but also cover feeds with subfeeds
    """
    if not os.path.isdir(dirpath):
        return False # not a directory
    ver_dir = ( os.listdir(dirpath)
              | where(lambda name: len(name)==4 and name.isdigit()) # 4-digit
              | select(lambda name: os.path.join(dirpath, name))
              | where(os.path.isdir) # feed ver is a dir
              | as_list ) # list of "feed_name/0001/versions"
    for dirname in ver_dir:
        for root, _dirs, files in os.walk(dirname):
            if root.rsplit(os.sep, 1)[-1] == 'versions' and \
               any(name.isdigit() for name in files): # all-digit files
                return True
    return False

def list_feed_vers(feedroot, feedname):
    """Assume the feed directory exists. Return the list of feed versions in
    descending order

    Args:
        feedroot (str): root dir of the feed repository
        feedname (str): name of feed, also as the directory under feedroot

    Returns:
        list of strings, each is a valid feed version
    """
    dirpath = os.path.join(feedroot, feedname)
    vers = ( os.listdir(dirpath)
           | where(lambda name: len(name)==4 and name.isdigit())
           | where(lambda path: os.path.isdir(os.path.join(dirpath, path)))
           | sort
           | reverse
           | as_list )
    return vers

def list_feed_subfeeds(feedroot, feedname, feedver, subfeednames=()):
    """Assume the feed data directory exists. Return the list of subfeed names
    in ascending order

    Args:
        feedroot (str): root dir of the feed repository
        feedname (str): name of feed, also as the directory under feedroot
        feedver (str): feed version, also as the directory under feedname
        subfeednames (list): string of list of strings of partial names of subfeed

    Returns:
        list of list of strings, each is a valid subfeed. If subfeednames is
        provided, only those under the provided partial subfeed name is returned
    """
    feeddir = os.path.join(feedroot, feedname, feedver)
    dirpath = os.path.join(feeddir, *subfeednames)
    if not os.path.isdir(dirpath):
        return [] # not a directory or not exists
    subfeeds = ( os.walk(dirpath)
               | where(lambda rootdirfile: "versions" in rootdirfile[1])
               | select(lambda rootdirfile: rootdirfile[0][len(feeddir):])
               | sort
               | select(lambda dirname: list(filter(None, dirname.split(os.sep))))
               | where(lambda dirparts: "versions" not in dirparts)
               | as_list )
    return subfeeds

def list_feed_data_vers(feedroot, feedname, feedver, subfeednames=None):
    """Assume the feed data directory exists. Return the list of data versions
    in descending order

    Args:
        feedroot (str): root dir of the feed repository
        feedname (str): name of feed, also as the directory under feedroot
        feedver (str): feed version, also as the directory under feedname
        subfeednames (list): string of list of strings of names of subfeed

    Returns:
        list of strings, each is a valid feed version
    """
    if subfeednames:
        if isinstance(subfeednames, str):
            subfeednames = [subfeednames]
        dirpath = [feedroot, feedname, feedver] + subfeednames + ['versions']
        dirpath = os.path.join(*dirpath)
    else:
        dirpath = os.path.join(feedroot, feedname, feedver, 'versions')
    if not os.path.isdir(dirpath):
        return [] # not a directory or not exists
    vers = ( os.listdir(dirpath)
           | where(lambda name: name.isdigit())
           | sort
           | reverse
           | as_list )
    return vers

def get_feed_data(feedroot, feedname, feedver, dataver, subfeednames=None, subpath=None):
    """Read a particular feed data version

    Args:
        feedroot (str): root dir of the feed
        feedname (str): name of the feed
        feedver (str): version of the feed
        dataver (str): numeric string of data version
        subfeednames (list): string of list of strings of names of subfeed
        subpath (str): file path under a data version, in case data version is a
                       directory

    Returns:
        opened file pointer to the feed's data
    """
    # This function is to isolate the actual feed handling from filesystem
    if subfeednames:
        if isinstance(subfeednames, str):
            subfeednames = [subfeednames]
        dirpath = [feedroot, feedname, feedver] + subfeednames + ['versions', dataver]
    else:
        dirpath = [feedroot, feedname, feedver, 'versions', dataver]
    if subpath:
        dirpath.append(subpath)
    return open(os.path.join(*dirpath))

def add_feed_data_ver(filename, feedroot, feedname, feedver, subfeednames=None, dataver=None, move=False):
    """Push in a file into a feed directory. It will create appropriate
    directories if not exists and move the `filename` into there and named as
    `dataver`.

    Args:
        filename (str): path to a feed, can either a file or a directory
        feedroot (str): root dir of the feed
        feedname (str): name of the feed
        feedver (str): 4-digit feed version
        subfeednames (list): string of list of strings of names of subfeed
        dataver (str): numeric string of version. Assumed to be monotonically
            increasing in chronological order. If None, it will be deduced from
            the current UTC timestamp in YYYYMMDDHHMMSS format.
        move (bool): Delete original file after moved into feed
    Returns:
        str of the version
    """
    if not dataver:
        dataver = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    assert isinstance(dataver, str) and dataver.isdigit()

    # prepare destination
    if subfeednames:
        if isinstance(subfeednames, str):
            subfeednames = [subfeednames]
        dirpath = [feedroot, feedname, feedver] + subfeednames + ['versions']
        dirpath = os.path.join(*dirpath)
    else:
        dirpath = os.path.join(feedroot, feedname, feedver, 'versions')
    os.makedirs(dirpath, exist_ok=True)
    isdir = os.path.isdir(filename)
    assert isdir or os.path.isfile(filename)
    tempdest = os.path.join(dirpath, "."+dataver)
    permdest = os.path.join(dirpath, dataver)
    assert not os.path.exists(tempdest) # also asserts tempdest!=filename
    assert not os.path.exists(permdest)

    # copy or move
    if move: # move dir/file
        shutil.move(filename, tempdest)
    elif isdir: # copy dir recursively
        shutil.copytree(filename, tempdest)
    else: # copy single file
        shutil.copyfile(filename, tempdest)
    shutil.move(tempdest, permdest)
    return dataver

# vim:set ts=4 sw=4 sts=4 tw=100 fdm=indent et:
