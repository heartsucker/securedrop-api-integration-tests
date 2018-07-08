#!/usr/bin/env bash
set -e
set -u

declare -r lang_version="$1"
declare -r source_url="$2"
declare -r journo_url="$3"

# because of stupid virtualenv
set +u

pyenv local "$lang_version"
rm -rf venv
virtualenv venv
source venv/bin/activate
pip install git+https://github.com/heartsucker/python-securedrop-api.git@develop
pip install pyotp
./it_test.py --source-url "$source_url" --journo-url "$journo_url"
