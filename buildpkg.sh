#!/bin/env bash

python3.9 -m build
python3.9 -m twine upload dist/*

rm -r "dist/"