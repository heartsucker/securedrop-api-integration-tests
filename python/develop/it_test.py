#!/usr/bin/env python

from argparse import ArgumentParser
from os import path
from pyotp import TOTP

from securedrop_api.auth import UserPassOtp
from securedrop_api.client import Client


def main():
    parser = ArgumentParser(path.basename(__file__))
    parser.add_argument('--source-url', required=True)
    parser.add_argument('--journo-url', required=True)
    args = parser.parse_args()

    totp = TOTP('JHCOGO7VCER3EJ4L')
    auth = UserPassOtp('journalist', 'WEjwn8ZyczDhQSK24YKM8C9a', totp.now())
    client = Client(args.journo_url, auth)


if __name__ == '__main__':
    main()
