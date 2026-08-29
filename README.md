# PyNovel Engine

Python-first visual novel engine targeting Windows, macOS and Linux.

## 0.3 capabilities

- readable `.vn` scripting language
- scene/title commands, backgrounds and characters
- dialogue and narration with typewriter effect
- clickable and keyboard choices
- labels and jumps
- variables with `=`, `+=`, `-=`, `*=`, `/=`
- safe expression evaluation
- `if / else / endif`
- music, sounds, waits and transitions
- save/load state with background, characters and history
- Auto and Skip modes
- mouse and keyboard input
- resizable window and F11 fullscreen
- pygame-ce runtime
- PySide6 desktop editor with project tree, text editing, asset preview, validation and run buttons
- pytest coverage for parser and expressions
- PyInstaller build helper and GitHub Actions matrix

## Install

```bash
python -m pip install -e .
pytest
```

## Run demo

```bash
python -m vnengine run examples/demo
# or
pynovel run examples/demo
```

## Open editor

```bash
pynovel-editor examples/demo
```

## Script example

```text
title "My First Novel"
background "assets/room.png"
character Alice "assets/alice.png" center
say Alice "Hello."
set affection = 2
set affection += 3
if affection >= 5
say Narrator "Unlocked branch!"
else
say Narrator "Keep playing."
endif
choice
"Continue": next
"End": ending
```

## Build standalone application

Install PyInstaller and build on the target OS:

```bash
python -m pip install pyinstaller
python tools/build.py examples/demo --name MyNovel
```

The CI workflow builds Windows, macOS and Linux artifacts separately because native desktop bundles should be produced on their target operating systems.
