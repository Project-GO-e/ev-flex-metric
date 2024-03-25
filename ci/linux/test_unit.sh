#!/usr/bin/env sh

. .venv/bin/activate
PYTHONPATH='src/' pytest --cov=src/ --cov-report=html:./unit_test_coverage/ -v test
