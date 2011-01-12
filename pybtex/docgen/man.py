# Copyright (c) 2009, 2010, 2011  Andrey Golovizin
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Based on autodoc_man.py from bzr-1.16.1.

"""Generate man pages for pybtex and pybtex-convert.
"""

from __future__ import with_statement

import os
import sys
from datetime import datetime

from pybtex.__version__ import version


def man_escape(string):
    """Escapes strings for man page compatibility"""
    result = string.replace("\\","\\\\")
    result = result.replace("`","\\`")
    result = result.replace("-","\\-")
    return result


def format_synopsis(main_obj):
    yield '.SH "SYNOPSIS"'
    yield '.B "%s"' % main_obj.prog
    for part in format_args(main_obj):
        yield part


def format_args(main_obj):
    for arg in main_obj.args.split():
        if arg.startswith('[') and arg.endswith(']'):
            yield '['
            yield '.I "%s"' % arg[1:-1]
            yield ']'
        else:
            yield '.I "%s"' % arg


def format_description(main_obj):
    yield '.SH "DESCRIPTION"'
    yield main_obj.long_description


def format_help(main_obj):
    opt_parser = main_obj.opt_parser
    for part in format_option_group(opt_parser, 'general optons', opt_parser.option_list):
        yield part
    for option_group in opt_parser.option_groups:
        for part in format_option_group(opt_parser, option_group.title, option_group.option_list):
            yield part


def format_option_group(opt_parser, name, options):
    yield '.SH "%s"' % name.upper()
    for option in options:
        for part in format_option(opt_parser, option):
            yield part


def format_option(opt_parser, option):
    yield '.TP'
    yield '.B "%s"' % opt_parser.formatter.format_option_strings(option)
    if option.help:
        yield option.help


man_head = r"""
.\"Man page for Pybtex (%(cmd)s)
.\"
.\" Generation time: %(timestamp)s
.\" Large parts of this file are autogenerated from the output of
.\"     "%(cmd)s --help"
.\"
.TH %(cmd)s 1 "%(datestamp)s" "%(version)s" "Pybtex"

.SH "NAME"
%(cmd)s - %(description)s
""".strip()

def format_head(main_obj):
    now = datetime.utcnow()
    yield man_head % {
        'cmd': main_obj.prog,
        'version': version,
        'description': main_obj.description,
        'datestamp': now.strftime('%Y-%m-%d'),
        'timestamp': now.strftime('%Y-%m-%d %H:%M:%S +0000'),
    }

def format_see_also(main_obj):
    yield '.SH "SEE ALSO"'
    yield '.UR http://pybtex.sourceforge.net/'
    yield '.BR http://pybtex.sourceforge.net/'


def write_manpage(outfile, main_obj):
    """Assembles a man page"""
    write(outfile, format_head(main_obj), escape=False)
    write(outfile, format_synopsis(main_obj))
    write(outfile, format_description(main_obj))
    write(outfile, format_help(main_obj))
    write(outfile, format_see_also(main_obj))


def write(outfile, lines, escape=True):
    for line in lines:
        outfile.write(man_escape(line) if escape else line)
        outfile.write('\n')


def generate_manpage(man_dir, main_obj):
    man_filename = os.path.join(man_dir, '%s.1' % main_obj.prog)
    with open(man_filename, 'w') as man_file:
        write_manpage(man_file, main_obj)


def generate_manpages(doc_dir):
    man_dir = os.path.join(doc_dir, 'man1')
    from pybtex.__main__ import main as pybtex
    from pybtex.database.convert.__main__ import main as pybtex_convert
    generate_manpage(man_dir, pybtex)
    generate_manpage(man_dir, pybtex_convert)