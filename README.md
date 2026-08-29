# PyNovel Engine

Python-first visual novel engine targeting Windows, macOS and Linux.

## 0.9 capabilities

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
- in-game menu with Resume, New Game, Save, Load, History, Settings, Main Menu and Quit
- five save slots
- persistent player profile (`profile.json`)
- title screen with New Game / Continue / Load / Settings / Quit
- Russian and English UI localization through JSON catalogs
- project-configurable UI theme through `theme.json`
- mouse and keyboard menu navigation
- Auto and Skip modes
- resizable window and F11 fullscreen
- pygame-ce runtime
- PySide6 desktop editor with project tree, script editing, asset preview and validation
- visual Scene editor with draggable character placement
- visual Dialogue graph editor with nodes and links
- dialogue graph JSON saved independently from the compiled script
- graph-to-`.vn` compiler with validation of missing targets
- pytest coverage for parser, expressions, scene data, dialogue graphs, menu/profile logic and animation tweening
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

## Runtime controls

- `Enter` / `Space`: continue
- `1-9`: choose option
- `Esc`: open menu
- `F5`: quick save slot 1
- `F9`: quick load slot 1
- `F7`: toggle skip
- `F8`: toggle auto
- `F11`: fullscreen

## UI theme

Put `theme.json` in the project root to customize interface colors. Example:

```json
{
  "background": [13, 16, 28],
  "panel": [18, 22, 34],
  "panel_border": [220, 220, 230],
  "text": [245, 245, 250],
  "muted_text": [165, 170, 185],
  "accent": [55, 70, 102],
  "accent_hover": [72, 88, 124]
}
```

## Localization

Project UI catalogs live in `locales/`, for example `ru.json` and `en.json`. Set the default language in `project.json` or the player profile.

## Animation script example

```text
title "My First Novel"
background "assets/room.png"
character Alice "assets/alice.png" center happy
expression Alice excited
move Alice left 0.45
scale Alice 1.08 0.35
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

## Documentation

- [Russian README](README_RU.md)
- [Packaging notes](packaging/README.md)
