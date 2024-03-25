#! /bin/bash

set -e
commands=(
    "CONFIG_PATH='./configs/1055.toml' PYTHONPATH='src/:' python3 -m ev_flex_metric.shifted_energy_profiles"
    "CONFIG_PATH='./configs/1212.toml' PYTHONPATH='src/:' python3 -m ev_flex_metric.shifted_energy_profiles"
)
parallel --jobs 4 ::: "${commands[@]}"

echo "All commands completed"
