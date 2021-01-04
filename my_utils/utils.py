#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application-agnostic utility functions
"""

import io
import logging
import mimetypes
import os
import os.path
import smtplib
import sys

__all__ = [
    "exception_hook", "print_tb_with_local", "supports_color", "get_logger",
    "readxml", "readkeyval", "readyaml", "email", "curl", "sieve", "flatten", "subdict"
]


def exception_hook(hooktype="trace"):
    """Replace system's exception hook

    Args:
        hooktype (str): The type of exception hook to register, any of "trace",
            "debug", "local" to mean exception log with traceback and exit only,
            launch post-mortem debugger, and print local variable value of each
            frame, respectively.
    """
    assert hooktype in ["trace", "debug", "local"]
    if hooktype == "trace":
        # reset system default
        sys.excepthook = sys.__excepthook__
    elif hooktype == "debug":
        def debughook(etype, value, tb):
            "Launch post-mortem debugger"
            import traceback, pdb
            traceback.print_exception(etype, value, tb)
            print() # make a new line before launching post-mortem
            pdb.pm() # post-mortem debugger
        sys.excepthook = debughook
    elif hooktype == "local":
        def dumphook(etype, value, tb):
            "Dump local variables at each frame of traceback"
            print_tb_with_local()
            sys.__excepthook__(etype, value, tb)
        sys.excepthook = dumphook

def print_tb_with_local():
    """Print stack trace with local variables. This does not need to be in
    exception. Print is using the system's print() function to stderr.
    """
    import traceback
    tb = sys.exc_info()[2]
    stack = []
    while tb:
        stack.append(tb.tb_frame)
        tb = tb.tb_next()
    traceback.print_exc()
    print("Locals by frame, innermost last", file=sys.stderr)
    for frame in stack:
        print("Frame {0} in {1} at line {2}".format(
            frame.f_code.co_name,
            frame.f_code.co_filename,
            frame.f_lineno), file=sys.stderr)
        for key, value in frame.f_locals.items():
            print("\t%20s = " % key, file=sys.stderr)
            try:
                if '__repr__' in dir(value):
                    print(value.__repr__(), file=sys.stderr)
                elif '__str__' in dir(value):
                    print(value.__str__(), file=sys.stderr)
                else:
                    print(value, file=sys.stderr)
            except:
                print("<CANNOT PRINT VALUE>", file=sys.stderr)

def supports_color():
    """Tells if the console (both stdout and stderr) supports ANSI color using a
    heuristic checking. Code adapted from Django. In Windows platform, a program
    called "ANSICON" is needed.

    Returns:
        True if we think the terminal supports ANSI color code. False otherwise.
    """
    if os.environ.get('TERM') == 'ANSI':
        return True # env var overridden result

    plat = sys.platform
    cygwin = "cygwin" in os.environ.get("HOME", "") # win python running in cygwin terminal
    supported = (plat != 'Pocket PC') and (plat != 'win32' or 'ANSICON' in os.environ)

    # isatty is not always implemented, #6223. Not checking stdout as this is
    # mostly for logging use only.
    is_a_tty = hasattr(sys.stderr, 'isatty') and sys.stderr.isatty()
    return cygwin or (supported and is_a_tty)

# ANSI colour code constants
ANSI_RESET = "\033[0m"
ANSI_COLOR = "\033[1;%dm"
ANSI_BOLD = "\033[1m"
(BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE) = range(30, 38)

def _loglevelcode(levelstring):
    """Convert a logging level string into the integer code.
    Python 3.2+ supports level strings but this way is more flexible

    Args:
        levelstring (str): anything with prefix "all", "not", "debug", "info",
                           "warn", "err", "except", "crit", or "fatal"
    Returns:
        int of the corresponding logging level according to the logging module
    """
    levelmap = {
        "all":   logging.NOTSET,
        "not":   logging.NOTSET,
        "debug": logging.DEBUG,
        "info":  logging.INFO,
        "warn":  logging.WARN,
        "err":   logging.ERROR,
        "except":logging.ERROR,
        "crit":  logging.CRITICAL,
        "fatal": logging.FATAL,
    }
    for prefix, levelcode in levelmap.items():
        if levelstring.lower().startswith(prefix):
            return levelcode
    return None # not recognized

def get_logger(root=None, level=logging.DEBUG, filename=None, filelevel=None,
               stream=None, console=True, reset=False):
    """Configurating the logging facilities to log possibly to both console and
    file. You should only run this once at the root level and subsequently use
    logging.getLogger() to get a subordinate logger.

    Args:
        root (str): root logger to set, default is the global root
        level (int): the logging level to use for console, default at debug. This also
                accepts string name of the logging level
        filename (str): if provided, log will be appended to the file
        filelevel (int): the logging level to use for file, default is same as console's level
        stream (file-like object): if provided, write log to a stream object,
               such as StringIO buffer
        console (bool): whether to print log to console
        reset (bool): delete all existing log handler of the root logger if set to True
    Returns:
        a python logger object
    """
    # reset string-type logging level into integers
    if isinstance(level, str):
        level = _loglevelcode(level)
    if level is None:
        level = logging.INFO
    assert isinstance(level, int)

    if isinstance(filelevel, str):
        filelevel = _loglevelcode(filelevel)
        if filelevel is None:
            filelevel = logging.INFO
    elif filelevel is None:
        filelevel = level
    assert isinstance(filelevel, int)

    # get logger and reset handlers if requested
    logger = logging.getLogger(root)
    if reset and logger.handlers:
        logger.handlers = [] # empty existing handlers
    # console handler
    consoleformat = "%(asctime)s|%(name)s(%(filename)s:%(lineno)d)|%(levelname)s|%(message)s"
    if not console:
        logger.addHandler(logging.NullHandler())
    else:
        shandler = logging.StreamHandler()
        shandler.setLevel(level)
        if not supports_color():
            shandler.setFormatter(logging.Formatter(consoleformat))
        else:
            colours = {"DEBUG":BLUE, "INFO":CYAN, "WARNING":YELLOW, "ERROR":RED, "CRITICAL":MAGENTA}
            class ColouredFormatter(logging.Formatter):
                "log message formatter to color messages according to levels"
                def format(self, record):
                    msg = logging.Formatter.format(self, record)
                    if record.levelname in colours:
                        msg = (ANSI_COLOR % colours[record.levelname]) + msg + ANSI_RESET
                    return msg
            shandler.setFormatter(ColouredFormatter(consoleformat))
        logger.addHandler(shandler)
    # file handler
    fileformat = "%(asctime)s|%(name)s(%(filename)s:%(lineno)d)|%(levelname)s|%(message)s"
    filetimeformat = "%Y-%m-%d %H.%M.%S"
    if filename:
        fhandler = logging.FileHandler(filename, encoding="utf8")
        fhandler.setLevel(filelevel)
        fhandler.setFormatter(logging.Formatter(fileformat, filetimeformat))
        logger.addHandler(fhandler)
    if stream:
        shandler = logging.StreamHandler(stream)
        shandler.setLevel(filelevel)
        shandler.setFormatter(logging.Formatter(fileformat, filetimeformat))
        logger.addHandler(shandler)
    # set logger's level to be min of both handlers'
    logger.setLevel(min(level, filelevel))
    return logger

def readxml(filename, retain_namespace=False):
    """Read XML from a file and optionally remove the namespace (default)

    Args:
        filename (str): XML file to read
        retain_namespace (bool): If set to True, the namespace info will be retained. Default False

    Returns:
        lxml etree DOM of the XML
    """
    from lxml import etree
    dom = etree.parse(os.path.expanduser(filename))
    if not retain_namespace:
        # XSLT from https://stackoverflow.com/questions/4255277
        xslt = """
            <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
                <xsl:output method="xml" indent="no"/>

                <xsl:template match="/|comment()|processing-instruction()">
                    <xsl:copy>
                      <xsl:apply-templates/>
                    </xsl:copy>
                </xsl:template>

                <xsl:template match="*">
                    <xsl:element name="{local-name()}">
                      <xsl:apply-templates select="@*|node()"/>
                    </xsl:element>
                </xsl:template>

                <xsl:template match="@*">
                    <xsl:attribute name="{local-name()}">
                      <xsl:value-of select="."/>
                    </xsl:attribute>
                </xsl:template>
            </xsl:stylesheet>
        """
        xslt_doc = etree.parse(io.BytesIO(bytes(xslt, "utf-8")))
        transform = etree.XSLT(xslt_doc)
        dom = transform(dom)
    return dom

def readkeyval(filename):
    """Load a text file of key=val lines and return a dictionary. Comments can
    be started with # char and run up to the end of line. Supposed to be used as
    a config file

    Args:
        filename (str): Filename, assumed accessible by open()
    Returns:
        Dictionary of the corresponding key=val context
    """
    COMMENT_CHAR, OPTION_CHAR = '#', '='
    options = {}
    with open(os.path.expanduser(filename), 'r') as fp:
        for line in fp:
            # remove comments from a line
            if COMMENT_CHAR in line:
                line, _ = line.split(COMMENT_CHAR, 1)
            # parse key=value
            if OPTION_CHAR in line:
                option, value = line.split(OPTION_CHAR, 1)
                options[option.strip()] = value.strip()
    return options

def readyaml(filename):
    """Load a YAML file and return a dictionary. Supposed to be used as a config
    file.

    Args:
        filename (str): Filename, assumed accessible and in YAML format

    Returns:
        Dictionary of the YAML file content

    Raises:
        IOError if cannot read filename, AssertionError if the YAML read is not a dictionary
    """
    import yaml
    data = yaml.load(open(os.path.expanduser(filename)))
    assert isinstance(data, dict)
    return data

def email(sender, recipient, subject, body, smtphost, smtpport=25,
          priority=3, cc=None, attachment=None, asbyte=False):
    """Send email

    Args:
        sender (str): email of sender
        recipient (str): email of recipient
        subject (str): subject line
        body (st): email body
        smtpHost (str): The SMTP host name
        smtpPort (int): SMTP port number, default 25
        priority (int): Priority of email, default 3
        cc (str): email of CC recipients
        attachment (list): Paths to files to attach in the email
        asbyte (bool): If set to True, no email will be sent but the formatted
                       email is returned as string
    Returns:
        The email message formatted for SMTP if asbyte is True, otherwise nothing
    """
    # TODO add bcc support
    if isinstance(priority, str):
        if priority.lower().startswith("high"):
            priority = 1
        elif priority.lower().startswith("low"):
            priority = 5
    assert not attachment or isinstance(attachment, list)
    assert isinstance(priority, int) and 1 <= priority <= 5
    assert isinstance(smtpport, int)

    from email.message import EmailMessage

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    if priority != 3:
        msg["X-Priority"] = priority # <3 means high and >3 means low
    if cc:
        msg['Cc'] = cc
    for path in attachment or []:
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        filename = os.path.split(path)[-1]
        with open(path, "rb") as fp:
            msg.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=filename)
    if not asbyte:
        smtp = smtplib.SMTP(smtphost, smtpport)
        smtp.send_message(msg)
        smtp.quit()
    else: # for debug, return message as string
        from email.policy import SMTP
        return msg.as_bytes(policy=SMTP)

def curl(url, data=None, method='get'):
    """Download one file from a web URL. The request is stateless, just like
    what the cURL tool would do.

    Args:
        url (str): URL to request
        data (dict): data to pass on into the request, such as the post body
        method (str): one of the six HTTP methods, "get", "put", "post",
                      "delete", "head", "options"
    Returns:
        requests.response object. We can get the content in binary or text using
        response.content or response.text respectively
    """
    import requests
    assert method in ["get", "put", "post", "delete", "head", "options"]
    requestfunction = getattr(requests, method)
    params = {}
    if data:
        params["data"] = data
    return requestfunction(url, **params)

def sieve(iterable, indicator):
    """Split an iterable into two lists by a boolean indicator function. Unlike
    `partition()` in iters.py, this does not clone the iterable twice. Instead,
    it run the iterable once and return two lists.

    Args:
        iterable: iterable of finite items. This function will scan it until the
                  end
        indicator: an executable function that takes an argument and returns a
                   boolean
    Returns:
        A tuple (positive, negative), which each items are from the iterable and
        tested with the indicator function
    """
    positive = []
    negative = []
    for item in iterable:
        (positive if indicator(item) else negative).append(item)
    return positive, negative

def flatten(sequence, types=None, checker=lambda x:hasattr(x,'__iter__')):
    """Flatten a sequence. By default, a sequence will be flattened until no element has __iter__
    attribute.

    Args:
        types: a data type or a tuple of data types. If provided, only elements of these types will
               be flattened
        checker: a function. If types is not provided, this checker will tell if an element should
                 be flattened

    Returns:
        This is a generator that recursively yields all elements in the input sequence
    """
    for x in sequence:
        if (types and isinstance(x, types)) or (not types and checker(x)):
            for z in flatten(x):
                yield z
        else:
            yield x

# strip down an input dict to keep only some specified keys
subdict = lambda _dict, _keys: {k:v for k,v in _dict.items() if k in _keys}

# vim:set ts=4 sw=4 sts=4 tw=100 fdm=indent et:
