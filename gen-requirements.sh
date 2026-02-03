#!/bin/sh
set -eu

python -m venv /opt/venv
/opt/venv/bin/pip install -U pip setuptools wheel
/opt/venv/bin/pip install -r requirements.in

# for test
/opt/venv/bin/ablog build -s /work/src -w /tmp

/opt/venv/bin/pip freeze > requirements.txt
