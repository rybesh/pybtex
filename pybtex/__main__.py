#!/usr/bin/env python

# Copyright (c) 2006, 2007, 2008, 2009, 2010, 2011  Andrey Golovizin
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

from os import path

from pybtex.cmdline import CommandLine, make_option


class PybtexCommandLine(CommandLine):
    prog = 'pybtex'
    args = '[options] auxfile.aux'
    description = 'BibTeX-compatible bibliography processor in Python'
    long_description = """

Pybtex reads citation information from a LaTeX .aux file and produces a
formatted bibliography. Pybtex understands BibTeX .bib and .bst style files and
can be used as a drop-in replacement for BibTeX.

Besides BibTeX .bib files, BibTeXML and YAML bibliography files are
supported.

It is also possible to define bibliography formatting styles in Python.

    """.strip()
    num_args = 1

    options = (
        (None, (
            make_option(
                '-f', '--bibliography-format', dest='bib_format',
                help='bibliograpy format (%plugin_choices)',
                type='load_plugin',
                plugin_group='pybtex.database.input',
                metavar='FORMAT',
            ),
            make_option(
                '-b', '--output-backend', dest='output_backend',
                help='output backend (%plugin_choices)',
                type='load_plugin',
                plugin_group='pybtex.backends',
                metavar='BACKEND',
            ),
            make_option(
                '-l', '--style-language', dest='style_language',
                help='style definition language to use (bibtex or python)',
                metavar='LANGUAGE',
            ),
            make_option(
                '--label-style', dest='label_style',
                help='label formatting style (%plugin_choices)',
                type='load_plugin',
                plugin_group='pybtex.style.labels',
                metavar='STYLE',
            ),
            make_option(
                '--name-style', dest='name_style',
                help='name formatting style (%plugin_choices)',
                type='load_plugin',
                plugin_group='pybtex.style.names',
                metavar='STYLE',
            ),
            make_option(
                '--abbreviate-names',
                action='store_true', dest='abbreviate_names',
                help='use abbreviated name formatting style',
            ),
            make_option(
                '--min-crossrefs',
                type='int', dest='min_crossrefs',
                help='include item after NUMBER crossrefs; default 2',
                metavar='NUMBER',
            ),
            make_option(
                '--terse', dest='verbose', action='store_false',
                help='ignored for compatibility with BibTeX',
            )
    )),
        ('Encoding options', (
            make_option(
                '-e', '--encoding', dest='encoding', metavar='ENCODING',
                help='default encoding',
            ),
            make_option('--bibtex-encoding', dest='bib_encoding', metavar='ENCODING'),
            make_option('--bst-encoding', dest='bst_encoding', metavar='ENCODING'),
            make_option('--output-encoding', dest='output_encoding', metavar='ENCODING'),
        )),
    )
    option_defaults = {
        'style_language': 'bibtex',
        'min_crossrefs': 2,
    }
    legacy_options = '-help', '-version', '-min-crossrefs', '-terse'

    def run(self, options, args):
        from pybtex.plugin import find_plugin

        filename = args[0]
        ext = path.splitext(filename)[1]
        if ext != '.aux':
            filename = path.extsep.join([filename, 'aux'])

        not_supported_by_bibtex = {
            'output_backend': 'output backends',
            'label_style': 'label styles',
            'name_style': 'name styles',
            'abbreviate_names': 'abbreviated names',
        }
        if options.style_language != 'python':
            for option, what_is_not_supported in not_supported_by_bibtex.items():
                if getattr(options, option):
                    self.opt_parser.error(
                        '%s are only supported by the Pythonic style engine (-l python)' % what_is_not_supported
                    )


        kwargs = {}
        if options.label_style:
            kwargs['label_style'] = find_plugin('pybtex.style.labels', options.label_style)
        if options.name_style:
            kwargs['name_style'] = find_plugin('pybtex.style.names', options.name_style)
        if options.output_backend:
            kwargs['output_backend'] = find_plugin('pybtex.backends', options.output_backend)
        if options.bib_format:
            kwargs['bib_format'] = find_plugin('pybtex.database.input', options.bib_format)
        kwargs['abbreviate_names'] = bool(options.abbreviate_names)
        kwargs['min_crossrefs'] = options.min_crossrefs
        for option in ('bib_encoding', 'output_encoding', 'bst_encoding'):
            value = getattr(options, option) or options.encoding
            if value:
                kwargs[option] = value

        if options.style_language == 'bibtex':
            from pybtex import bibtex as engine
        elif options.style_language == 'python':
            import pybtex as engine
        else:
            self.opt_parser.error('unknown style language %s' % options.style_language)

        engine.make_bibliography(filename, **kwargs)

main = PybtexCommandLine()

if __name__ == '__main__':
    main()
