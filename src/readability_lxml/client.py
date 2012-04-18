import argparse
import sys

from readability_lxml import VERSION
from readability_lxml.readability import Document


def parse_args():
    desc = "fast python port of arc90's readability tool"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--version',
        action='version', version=VERSION)

    parser.add_argument('-v', '--verbose',
        action='store_true',
        default=False,
        help="Increase logging verbosity to DEBUG.")

    parser.add_argument('-u', '--url',
        action='store',
        default=None,
        help="Indicate that this is a url path.")

    parser.add_argument('path', metavar='P', type=str, nargs=1,
        help="The url or file path to process in readable form.")

    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    target = None
    if args.url:
        import urllib
        target = urllib.urlopen(args.path[0])
    else:
        target = open(args.path[0], 'rt')

    enc = sys.__stdout__.encoding or 'utf-8'

    try:
        doc = Document(target.read(),
            debug=args.verbose,
            url=args.url)
        print doc.summary().encode(enc, 'replace')

    finally:
        target.close()


if __name__ == '__main__':
    main()
