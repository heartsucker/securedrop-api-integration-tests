#!/usr/bin/env bash
set -e
set -u

declare -r lang_version="$1"
declare -r source_url="$2"
declare -r journo_url="$3"

# because of stupid virtualenv
set +u

rm -rf venv .python-version
pyenv local "$lang_version"

virtualenv venv
source venv/bin/activate

pip install -r requirements.txt

./it_test.py --source-url "$source_url" --journo-url "$journo_url"
