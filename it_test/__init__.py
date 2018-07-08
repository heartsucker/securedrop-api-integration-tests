import fcntl
import os
import subprocess
import sys

from argparse import ArgumentParser
from contextlib import contextmanager
from os import path
from typing import List

from .sdk import SDKS, Sdk, SdkVersion, SecureDropVersion

REPO_URL = 'https://github.com/freedomofpress/securedrop.git'
ROOT = path.abspath(path.join(path.dirname(__file__), os.pardir))
WORKSPACE = path.join(ROOT, '.workspace')
SOURCE_CODE = path.join(WORKSPACE, 'securedrop')

ALL_TESTS = ['{}:{}:{}:{}'.format(
                sdk.name, sdk_version.version, lang_version, sd_version.version)
             for sdk in SDKS
             for sdk_version in sdk.versions
             for sd_version in sdk_version.sd_versions
             for lang_version in sdk_version.lang_versions]


def colorize(msg, color, bold=False):
    shell_colors = {
        'gray': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37',
        'crimson': '38',
        'highlighted_red': '41',
        'highlighted_green': '42',
        'highlighted_brown': '43',
        'highlighted_blue': '44',
        'highlighted_magenta': '45',
        'highlighted_cyan': '46',
        'highlighted_gray': '47',
        'highlighted_crimson': '48'
    }
    attrs = [shell_colors[color]]
    if bold:
        attrs.append('1')
    return '\x1b[{}m{}\x1b[0m'.format(';'.join(attrs), msg)


def error(msg) -> None:
    print(colorize(msg, 'red', True))


def warn(msg) -> None:
    print(colorize(msg, 'yellow', True))


def info(msg) -> None:
    print(colorize(msg, 'blue', True))


def success(msg) -> None:
    print(colorize(msg, 'green', True))


class Error(Exception):
    pass


def main() -> None:
    try:
        _main()
    except Error as e:
        error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        warn('\nInterrupted.')
        sys.exit(1)


def _main() -> None:
    args = arg_parser().parse_args()

    with acquire_lock():
        if args.fetch:
            get_source_code(args.repo)

        for test in (args.test or ALL_TESTS):
            (sdk, sdk_version, lang_version, sd_version) = test.split(':')

            # lazy search
            (sdk,) = [x for x in SDKS if x.name == sdk]
            (sdk_version, ) = [x for x in sdk.versions if x.version == sdk_version]
            (sd_version, ) = [x for x in sdk_version.sd_versions if x.version == sd_version]

            run_test(sdk, sdk_version, lang_version, sd_version)


def run_test(sdk: Sdk,
             sdk_version: SdkVersion,
             lang_version: str,
             sd_version: SecureDropVersion) -> None:
    sdk.fetch_lang_version(lang_version)

    with live_server(sd_version) as (source_url, journo_url):
        test_dir = path.join(ROOT, sdk.name, sdk_version.version)
        cmd = [
            './test.sh',
            lang_version,
            source_url,
            journo_url,
        ]
        subprocess.check_call(cmd, cwd=test_dir)


@contextmanager
def acquire_lock() -> None:
    with open(path.join(WORKSPACE, 'lock'), 'w') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX)
        except (OSError, IOError):
            error('Failed to acquire lock. Are the tests already running?')
        yield


def get_source_code(repo: str) -> None:
    info('Fetching source code.')
    if not path.exists(WORKSPACE):
        os.makedirs(WORKSPACE)
    elif not path.isdir(WORKSPACE):
        raise Error('Not a directory: {}'.format(WORKSPACE))

    if path.exists(SOURCE_CODE):
        subprocess.check_call(['git', 'fetch'], cwd=SOURCE_CODE)
    else:
        subprocess.check_call(['git', 'clone', repo, SOURCE_CODE])


@contextmanager
def live_server(sd_version: SecureDropVersion) -> (str, str):
    info('Booting server.')
    # "clean" the repo
    subprocess.check_call(['git', 'checkout', '--', '.'], cwd=SOURCE_CODE)

    # the get version we want
    subprocess.check_call(['git', 'checkout', sd_version.version], cwd=SOURCE_CODE)
    subprocess.check_call(['git', 'pull'], cwd=SOURCE_CODE)

    # run the dev server
    try:
        sd_version.run_cmd(SOURCE_CODE)
        yield ('http://localhost:8080', 'http://localhost:8081')
    finally:
        sd_version.kill_cmd(SOURCE_CODE)


def arg_parser() -> ArgumentParser:

    parser = ArgumentParser('it-test',
                            description='Run the SecureDrop API integration tests.')
    parser.add_argument('-t', '--test',
                        help=('Tests to run (format sdk:sdk_version:lang_version:sd_version) '
                              '(Default: all)'),
                        default=[],
                        choices=ALL_TESTS,
                        action='append')
    parser.add_argument('-r', '--repo',
                        help='SecureDrop git repo (Default: {})'.format(REPO_URL),
                        default=REPO_URL)
    parser.add_argument('--no-fetch',
                        help='Disable repo fetching.',
                        action='store_false',
                        dest='fetch')
    return parser
