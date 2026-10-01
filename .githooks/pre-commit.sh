#!/usr/bin/env bash
uv pip freeze > requirements.txt
git add requirements.txt
