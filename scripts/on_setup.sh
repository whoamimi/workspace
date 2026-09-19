#!/usr/bin/env bash
# Setup Script for cloning to new macbook

# To create a brand new environment in current directory, uncomment the following line:
python -m venv .venv

# Activate the virtual environment in running terminal
source .venv/bin/activate

pip install --upgrade pip
pip install -r ../requirements.txt