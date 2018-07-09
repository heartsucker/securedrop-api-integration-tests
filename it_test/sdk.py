import attr
import requests
import subprocess
import time

from os import path
from typing import List
from requests.exceptions import ConnectionError

from .utils import info

"""
Tests are done as a subset of the cross product of:
    - SDK name
    - SDK version
    - Language version
    - SecureDrop version

For example:
    - python
        - develop
            - 3.4
                - develop
                - 0.9.0
            - 3.5
                - develop
                - 0.9.0
    - rust
        - develop
            - 1.26
                - develop
                - 0.9.0
            - 1.27
                - develop
                - 0.9.0

Old versions of the SDK may not have to support new versions of the language.
"""


@attr.s
class SecureDropVersion:
    version = attr.ib(type=str)

    def run_cmd(self, code_dir: str) -> None:
        raise NotImplementedError

    def kill_cmd(self, code_dir: str) -> None:
        raise NotImplementedError


@attr.s
class SdkVersion:
    version = attr.ib(type=str)
    lang_versions = attr.ib(type=List[str])
    sd_versions = attr.ib(type=List[SecureDropVersion])


@attr.s
class Sdk:
    name = attr.ib(type=str)
    versions = attr.ib(type=List[SdkVersion])

    def fetch_lang_version(self, lang_version: str) -> None:
        if self.name == 'python':
            subprocess.check_call(['pyenv', 'install', '-s', lang_version])
        elif self.name == 'rust':
            subprocess.check_call(['rustup', 'toolchain', 'install', lang_version])
        else:
            raise NotImplementedError('Unknown SDK type: {}'.format(self.name))


class SecureDropVersionDevelop(SecureDropVersion):

    def __init__(self, *nargs, **kwargs) -> None:
        # TODO this should be develop
        super().__init__('journalist-api-0.9.0')
        self.__docker_hash = None

    def run_cmd(self, code_dir: str) -> None:
        tag = 'securedrop-api/integration-test:{}'.format(self.version)
        cmd = ['docker', 'build', '--tag', tag, '.']
        subprocess.check_call(cmd, cwd=path.join(code_dir, 'securedrop'))

        cmd = [
            'docker', 'run', '-t', '-d',
            '--expose', '8080', '--expose', '8081',
            '--publish', '127.0.0.1:8080:8080', '--publish', '127.0.0.1:8081:8081',
            '-v', code_dir + '/securedrop:/src', '-w', '/src',
            tag, 'bin/run',
        ]
        self.__docker_hash = subprocess.check_output(cmd).decode('utf-8').strip()

        attempts = 30
        while True:
            try:
                attempts -= 1
                requests.get('http://localhost:8081/api/v1')
                break
            except ConnectionError as e:
                if attempts <= 0:
                    raise e
                else:
                    info('Waiting for server to boot.')
                    time.sleep(1)

    def kill_cmd(self, _code_dir: str) -> None:
        if self.__docker_hash is not None:
            cmd = ['docker', 'rm', '-f', self.__docker_hash]
            subprocess.check_output(cmd)


sd_develop = SecureDropVersionDevelop()

SDKS = [
    Sdk(
        'python',
        [
            SdkVersion(
                'develop',
                # development versions of the python SDK target latest of 3.4, 3.5, and 3.6
                ['3.4.8', '3.5.5', '3.6.6'],
                [sd_develop],
            ),
        ]
    ),
    Sdk(
        'rust',
        [
            SdkVersion(
                'develop',
                # development versions of the rust SDK target the head of these channels
                ['stable', 'beta', 'nightly'],
                [sd_develop],
            ),
        ],
    ),
]
