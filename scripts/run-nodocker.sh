#!/bin/bash

pipenv install || pip3 install -r requirements.txt
cd src
python3 __main__.py
