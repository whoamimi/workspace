#!/usr/bin/env zsh

uv pip freeze > requirements.txt
git add requirements.txt
