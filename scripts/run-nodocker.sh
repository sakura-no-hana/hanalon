#!/bin/bash

curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
poetry install
cd src
poetry run python __main__.py
