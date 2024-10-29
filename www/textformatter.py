
import re


def reportformat(txt):
    """
    Convert the given output report into an appropriate string.
    """
    m = re.match('<[A-Za-z]*>', txt)

    if m:
        # This is probably HTML
        return txt
    elif '\x1B' in txt:
        # This is probably formatted terminal output
        return format_terminal(txt)
    else:
        return f'<pre>{txt}</pre>'
        

def format_terminal(txt):
    """
    Convert terminal formatted output to HTML.
    """
    clrs = {
        '\x1B[0;30m': '<span class=".bash-0-30">',
        '\x1B[1;30m': '<span class=".bash-1-30">',
        '\x1B[0;31m': '<span class=".bash-0-31">',
        '\x1B[1;31m': '<span class=".bash-1-31">',
        '\x1B[0;32m': '<span class=".bash-0-32">',
        '\x1B[1;32m': '<span class=".bash-1-32">',
        '\x1B[0;33m': '<span class=".bash-0-33">',
        '\x1B[1;33m': '<span class=".bash-1-33">',
        '\x1B[0;34m': '<span class=".bash-0-34">',
        '\x1B[1;34m': '<span class=".bash-1-34">',
        '\x1B[0;35m': '<span class=".bash-0-35">',
        '\x1B[1;35m': '<span class=".bash-1-35">',
        '\x1B[0;36m': '<span class=".bash-0-36">',
        '\x1B[1;36m': '<span class=".bash-1-36">',
        '\x1B[0;37m': '<span class=".bash-0-37">',
        '\x1B[1;37m': '<span class=".bash-1-37">',
        '\x1B[0m':    '</span>'
    }

    s = txt
    for b, h in clrs.items():
        s = s.replace(b, h)

    return s


