# PyNovel Engine

Python visual novel engine for Windows, macOS and Linux.

## MVP
- `.vn` dialogue scripting
- scenes, backgrounds, characters
- choices and labels/jumps
- variables and conditional branches
- save/load state
- pygame-ce runtime
- PySide6 project viewer/editor shell

## Run
```bash
python -m pip install -e .
python -m vnengine run examples/demo
python editor/main.py examples/demo
pytest
```
