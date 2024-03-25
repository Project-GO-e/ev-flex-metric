#!/usr/bin/env sh

. .venv/bin/activate

rm -Rf ./dist/
mkdir ./dist/
pyinstaller --hidden-import fastparquet -p src/ --onedir -y -n ev-flex-metric src/ev_flex_metric/shifted_energy_profiles.py
cp README.md ./dist/
cp -R ./package_files/* ./dist/
