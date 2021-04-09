#!/bin/bash

pip3 install poetry
poetry install
cd src
python3 __main__.py
