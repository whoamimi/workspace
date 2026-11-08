#!/usr/bin/env zsh

./git_dir_tree.sh

uv pip freeze > requirements.txt
git add requirements.txt