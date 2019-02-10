# !./translate_venv/bin/python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from main import TranslatePO


def main():
    parser = ArgumentParser(description='PO File Translator')
    parser.add_argument('path', action='store', type=str, help='File Path')
    parser.add_argument('-s', '--src', action='store', type=str, help='From')
    parser.add_argument('-dest', '--dest', action='store', type=str, help='To')
    parser.add_argument('-p', '--proxy_size', action='store',
                        type=int, help='Proxy Size')
    parser.add_argument('-t', '--th_size', action='store',
                        type=int, help='Thread Size')

    args = parser.parse_args()

    dest = args.dest or 'de'
    src = args.src or 'auto'
    proxy_size = args.proxy_size or 50
    th_size = args.th_size or 20

    trans = TranslatePO(dest=dest, src=src,
                        proxy_size=proxy_size, th_size=th_size)
    trans.po_translate(args.path)


if __name__ == '__main__':
    main()
