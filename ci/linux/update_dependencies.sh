#!/usr/bin/env sh

. .venv/bin/activate
pip-compile -U -o ./requirements.txt ./requirements.in
pip-compile -U -o ./dev-requirements.txt ./dev-requirements.in
