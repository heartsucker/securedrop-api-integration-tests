import attr

from typing import List

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
    run_cmd = attr.ib(type=List[str])
    run_dir = attr.ib(type=str)


@attr.s
class SdkVersion:
    version = attr.ib(type=str)
    lang_versions = attr.ib(type=List[str])
    sd_versions = attr.ib(type=List[SecureDropVersion])


@attr.s
class Sdk:
    name = attr.ib(type=str)
    versions = attr.ib(type=List[SdkVersion])

    def fetch_lang_version(self, version: str) -> None:
        if self.name == 'python':
            subprocess.check_call(['pyenv', 'install', version])
        elif self.name == 'rust':
            subprocess.check_call(['rustup', 'toolchain', 'install', version])
        else:
            raise NotImplementedError('Unknown SDK type: {}'.format(self.name))


sd_develop = SecureDropVersion('develop', ['make', 'dev'], 'securedrop')

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
