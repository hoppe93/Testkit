# Logging facility for testkit

from datetime import datetime
import sys


outlog = None
errlog = None
deinit_out = False
deinit_err = False
use_colors = False


def init(outfile=sys.stdout, errfile=sys.stderr, colors=False):
    global use_colors, outlog, errlog

    use_colors = colors

    if type(outfile) == str:
        outlog = open(outfile, 'a')
        outlog.reconfigure(write_through=True)
        deinit_out = True
    else:
        outlog = outfile

    if type(errfile) == str:
        if errfile == outfile:
            errlog = outlog
        else:
            errlog = open(errfile, 'a')
            errlog.reconfigure(write_through=True)
            deinit_err = True
    else:
        errlog = errfile


def deinit():
    """
    De-initialize the logging module.
    """
    if deinit_out:
        outlog.close()
    if deinit_err:
        errlog.close()


def _logmsg(file, pre, msg):
    """
    Write a message to the log.
    """
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file.write(f'{pre} {ts}: {msg}\n')
    

def error(msg):
    """
    Print an error message to the log.
    """
    if use_colors:
        errtxt = '\x1B[1;31m[ERROR]\x1B[0m '
    else:
        errtxt = '[ERROR] '

    _logmsg(errlog, errtxt, msg)
        

def info(msg):
    """
    Print an info message to the log.
    """
    if use_colors:
        inftxt = '\x1B[1;34m[INFO]\x1B[0m '
    else:
        inftxt = '[INFO] '

    _logmsg(outlog, inftxt, msg)


def warning(msg):
    """
    Print a warning to the log.
    """
    if use_colors:
        wartxt = '\x1B[1;33m[WARNING]\x1B[0m '
    else:
        wartxt = '[WARNING] '

    _logmsg(errlog, wartxt, msg)


