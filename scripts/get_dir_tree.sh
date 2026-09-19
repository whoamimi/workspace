#!/usr/bin/env bash
# This script is intended to be run after the main script has completed, to generate the workspace directory's tree

# -L / max-depth: limit the depth of the directory tree to 4 levels
# -d / dirs-only: only show directories, not files
# Output the directory structure to a file for later reference
tree -L 4 -d -I '__pycache__|.venv|node_modules|plug-mimi' > project_tree.txt