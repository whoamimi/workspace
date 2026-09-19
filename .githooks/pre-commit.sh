#!/usr/bin/env bash
python -m pip freeze > requirements.txt
git add requirements.txt