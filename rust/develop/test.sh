#!/usr/bin/env bash
set -e
set -u

declare -r lang_version="$1"
declare -r source_url="$2"
declare -r journo_url="$3"

rustup run "$lang_version" cargo run -- "$source_url" "$journalist_url"
