# PyNovel Engine

Python-first visual novel engine targeting Windows, macOS and Linux.

## 0.6 capabilities

- readable `.vn` scripting language
- scene/title commands, backgrounds and characters
- dialogue and narration with typewriter effect
- clickable and keyboard choices
- labels, jumps and variables
- safe expression evaluation with `if / else / endif`
- music, sounds, waits and transitions
- character expressions plus `expression`, `move`, and `scale` commands
- eased character position and scale tweening
- save/load state with background, characters, expressions and history
- Auto and Skip modes
- resizable window and F11 fullscreen
- pygame-ce runtime
- PySide6 desktop editor with project tree, script editing, asset preview and validation
- visual Scene editor with draggable character placement
- visual Dialogue graph editor with nodes and links
- dialogue graph JSON saved independently from the compiled script
- graph-to-`.vn` compiler with validation of missing targets
- pytest coverage for parser, expressions, scene data, dialogue graphs and animation tweening
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

The editor has Script, Scene and Dialogue tabs. In Scene, place characters visually. In Dialogue, build the branching story graph, edit node properties, move nodes, save `dialogue.json`, then compile the graph to `game.vn`.

## Animation script example

```text
title "My First Novel"
background "assets/room.png"
character Alice "assets/alice.png" center happy
move Alice left 0.45
scale Alice 1.08 0.35
expression Alice excited
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
