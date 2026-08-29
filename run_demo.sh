#!/bin/sh
set -e
python -m pip install -e .
python -m vnengine.cli examples/demo
