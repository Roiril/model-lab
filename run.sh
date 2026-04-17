#!/usr/bin/env bash
# Usage: ./run.sh models/foo/model.py
BLENDER="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
"$BLENDER" --background --python "$1"
