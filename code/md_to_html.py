#!/usr/bin/env python3
#
import markdown
import argparse

version = 'v0.0.2'

m2hparser = argparse.ArgumentParser(
    description = '''DESCRIPTION: This simple Python app converts a markdown file to html.
    Specify the input and output filenames with path info as needed.  
    The input file normally would have a .md extension.  Check --help if you need it.
    '''
)
m2hparser.add_argument("-i", "--input", help="The path and complete filename of the input (.md) file.", action="store")
m2hparser.add_argument("-o", "--output", help="The path and complete filename of the output (.html) file.", action="store")
m2hargs = m2hparser.parse_args()

with open(m2hargs.input, 'r') as f:
    text = f.read()
    html = markdown.markdown(text, extensions=['md_in_html'])

with open(m2hargs.output, 'w') as f:
    f.write(html)
