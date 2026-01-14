# Contributing

This repository is a deterministic tooling project. Keep changes small, testable, and ASCII-only.

## Requirements

Python 3.10+.

Install dependencies:

pip install -e .

or

pip install -r requirements.txt

## Run tests

python -m pytest

## CLI smoke tests

python -m marcopolo.cli draft examples/marco.md --out out
python -m marcopolo.cli verify examples/marco.md examples/polo.md --out out

## Style

Prefer clarity over cleverness. Keep behavior deterministic by default.
