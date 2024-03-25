#!/bin/bash
. ./.venv/bin/activate
CONFIG_PATH="./config.toml" PYTHONPATH="src/:" python3 -m ev_flex_metric.shifted_energy_profiles
