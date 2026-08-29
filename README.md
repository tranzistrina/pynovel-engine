# PyNovel Engine

Python-first visual novel engine targeting Windows, macOS and Linux.

## 0.2 MVP capabilities

- readable `.vn` scripting language
- scenes, backgrounds and characters
- dialogue and narration
- choices, labels and jumps
- variables and safe expression evaluation
- `if / else / endif`
- music and sound hooks
- wait and transition actions
- save/load state
- dialogue history in saves
- auto and skip modes
- keyboard and mouse input
- pygame-ce runtime
- PySide6 desktop editor shell
- script validation
- pytest tests
- PyInstaller build helper and CI matrix

## Install

```bash
python -m pip install -e .
pytest
```

## Run the demo

```bash
python -m vnengine run examples/demo
# or
pynovel run examples/demo
```

## Editor

```bash
pynovel-editor examples/demo
```

## `.vn` example

```text
label start
background "assets/room.png"
character Alice "assets/alice.png" center
say Alice "Hello."
set affection = 2
if affection >= 2
say Narrator "Unlocked branch!"
endif
choice
"Continue": next
"End": ending
```

## Packaging

Build on the target OS with PyInstaller:

```bash
python -m pip install pyinstaller
python tools/build.py examples/demo --name MyNovel
```

Builds are platform-native because Python/SDL application bundles should be produced on Windows, macOS and Linux separately.
