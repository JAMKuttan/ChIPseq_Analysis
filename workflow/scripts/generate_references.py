#!/usr/bin/env python

'''Make header for HTML of references.'''

import argparse
import subprocess
import shlex
import logging

EPILOG = '''
For more details:
        %(prog)s --help
'''

# SETTINGS

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False
logger.setLevel(logging.INFO)


def get_args():
    '''Define arguments.'''

    parser = argparse.ArgumentParser(
        description=__doc__, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-r', '--reference',
                        help="The reference file (markdown format).",
                        required=True)

    parser.add_argument('-o', '--output',
                        help="The out file name.",
                        default='references')

    args = parser.parse_args()
    return args


def main():
    args = get_args()
    reference = args.reference
    output = args.output

    out_filename = output + '_mqc.txt'

    # Header for HTML
    print('''
        # id: 'References'
        # section_name: 'References'
        # description: 'This section describes references for the tools used.'
        # plot_type: 'html'
        '''
    , file = open(out_filename, "w")
    )

    # Turn Markdown into HTML
    references_html = 'bash -c "pandoc {} >> {}"'
    references_html = references_html.format(reference, out_filename)
    subprocess.check_call(shlex.split(references_html))


if __name__ == '__main__':
    main()
