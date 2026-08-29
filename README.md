# PyNovel Engine

> Cross-platform, Python-first visual novel engine and editor for Windows, macOS and Linux.
>
> Кроссплатформенный движок и редактор визуальных новелл на Python для Windows, macOS и Linux.

## English

PyNovel Engine is a Python-first visual novel toolkit with readable scripting, visual scene/dialogue/UI/animation editing, asset management, live graphical animation preview, an extensible runtime API, dynamic UI bindings, deterministic scheduling/RNG primitives, and a portable runtime.

### Current version: 0.31.0

### Extension API

External games can build on public engine APIs without adding game-specific rules to the core runtime. Available primitives include `GameSystem`, `EventBus`, `StateRegistry`, `SceneStack`, `CommandRegistry`, `GameScheduler`, `InputMap`, map/pathfinding/selection models, and `DeterministicRNG`.

### Dynamic UI bindings

`ui.json` can bind widget properties to explicit state paths:

```json
{
  "bindings": [
    {"widget": "supplies_label", "property": "text", "state": "strategy.supplies", "transform": "str"},
    {"widget": "legitimacy_label", "property": "text", "state": "campaign.legitimacy", "transform": "percent"}
  ]
}
```

Supported transforms are `str`, `int`, `float`, and `percent`.

### Features

- readable `.vn` scripting;
- scenes, backgrounds, characters and expressions;
- dialogue, narration, choices, labels and jumps;
- variables and safe expressions with `if / else / endif`;
- music, sound, waits, transitions and tween animations;
- direct `rotate <character> <degrees> <duration>` tween command;
- save/load, history, five slots and persistent player profile;
- title screen, in-game menu and localization;
- runtime UI widgets: `Panel`, `Label`, `Image`, `TextBox`, `Button`;
- explicit dynamic state-to-widget bindings;
- anchors, percentage dimensions, visibility and z-order;
- declarative `ui.json` interfaces and button actions;
- visual Scene, Dialogue and UI editors;
- UI hierarchy with safe reparenting and unique-id cloning;
- multi-selection and group transforms;
- box-selection geometry and group bounding-box transforms;
- Asset Catalog and Asset Browser with search, filtering, preview, path copy and drag-and-drop;
- scene/UI asset drops that create project objects automatically;
- animation timelines with tracks, keyframes, easing, playback and looping;
- animated `x`, `y`, `scale`, `opacity`, and `rotation` properties;
- Animation Editor with tracks, keyframes, playhead and live graphical preview;
- runtime `animation.json` player and `.vn` animation commands;
- extensible systems, events, state, commands and scene stack;
- deterministic scheduler and serializable RNG primitives;
- PyInstaller helper and GitHub Actions build support.

### Install

```bash
python -m pip install -e .
pytest
```

### Run demo

```bash
python -m vnengine run examples/demo
pynovel run examples/demo
```

### Open editor

```bash
pynovel-editor examples/demo
```

The editor contains **Script**, **Scene**, **Dialogue**, **UI**, **Animation**, and **Assets** workflows.

### Asset pipeline

```bash
pynovel assets scan examples/demo
```

### Build

```bash
python -m pip install pyinstaller
python tools/build.py examples/demo --name MyNovel
```

Build native bundles separately on Windows, macOS and Linux.

### inhRPG compatibility

See [`docs/INHRPG_SUPPORT.md`](docs/INHRPG_SUPPORT.md) for the compatibility roadmap. `inhRPG` remains a separate project and owns its campaign rules, factions, armies, economy, map content and mini-games.

---

## Русский

PyNovel Engine — кроссплатформенный движок и редактор визуальных новелл на Python для Windows, macOS и Linux. Помимо VN-функций, движок предоставляет расширяемый runtime API для внешних игр.

### Текущая версия: 0.31.0

Внешний проект может использовать `GameSystem`, `EventBus`, `StateRegistry`, `SceneStack`, `CommandRegistry`, `GameScheduler`, `InputMap`, модели карты/pathfinding/selection и `DeterministicRNG`, не добавляя правила конкретной игры в ядро.

### Dynamic UI bindings

`ui.json` может связывать свойства виджетов с явными путями состояния:

```json
{
  "bindings": [
    {"widget": "supplies_label", "property": "text", "state": "strategy.supplies", "transform": "str"},
    {"widget": "legitimacy_label", "property": "text", "state": "campaign.legitimacy", "transform": "percent"}
  ]
}
```

Поддерживаются преобразования `str`, `int`, `float` и `percent`.

### Возможности

- человекочитаемый язык сценариев `.vn`;
- сцены, фоны, персонажи и выражения;
- диалоги, повествование, выборы, `label` и `jump`;
- переменные и безопасные выражения;
- музыка, звуки, ожидания, переходы и tween-анимации;
- сохранение/загрузка, история, слоты и профиль игрока;
- локализация и меню;
- UI-компоненты runtime;
- динамические привязки state → UI;
- hierarchy, multi-selection и групповые трансформации;
- Asset Catalog, Asset Browser и drag-and-drop;
- animation timeline и графический preview;
- расширяемые системы, события, состояние, команды и scene stack;
- deterministic scheduler и serializable RNG;
- сборка через PyInstaller и GitHub Actions.

### Установка

```bash
python -m pip install -e .
pytest
```

### Запуск

```bash
pynovel run examples/demo
pynovel-editor examples/demo
```

### Совместимость с inhRPG

См. [`docs/INHRPG_SUPPORT.md`](docs/INHRPG_SUPPORT.md). `inhRPG` остаётся отдельным проектом и отвечает за собственные правила кампании, фракции, армии, экономику, карту и мини-игры.

### Документация

- [English](README.md)
- [Русский](README_RU.md)
- [Changelog](CHANGELOG.md)
