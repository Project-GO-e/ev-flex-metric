#!/usr/bin/env sh

. .venv/bin/activate
mypy ./src/ ./test/
