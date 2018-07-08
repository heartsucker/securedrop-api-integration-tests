#!/usr/bin/env python

from argparse import ArgumentParser
from os import path

from securedrop_api.client import Client, UserPassOtp


def main():
    parser = ArguentParser(path.basename(__file__))
    paser.add_argument('--source-url', required=True)
    paser.add_argument('--journo-url', required=True)
    args = parser.parse_args()

    auth = UserPassOtp('', '', '')
    client = Client(args.source_url, auth)


if __name__ == '__main__':
    main()
