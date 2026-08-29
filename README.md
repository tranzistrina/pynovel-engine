# PyNovel Engine

> Cross-platform, Python-first visual novel engine and editor for Windows, macOS and Linux.
>
> Кроссплатформенный движок и редактор визуальных новелл на Python для Windows, macOS и Linux.

## English

PyNovel Engine is a Python-first visual novel toolkit focused on readable scripting, visual editing and a portable runtime.

### Current version: 0.19.0

### Current capabilities

- readable `.vn` scripting language;
- scenes, backgrounds and characters;
- dialogue, narration and typewriter effect;
- clickable and keyboard choices;
- labels, jumps, variables and safe expressions;
- `if / else / endif`;
- music, sound, waits and transitions;
- character expressions, movement and scaling with tweening;
- save/load with background, character state and history;
- five save slots and persistent player profile;
- title screen and in-game menu;
- Russian and English localization through JSON catalogs;
- configurable UI theme through `theme.json`;
- runtime UI widgets: `Panel`, `Label`, `Image`, `TextBox`, `Button`;
- anchors, percentage dimensions, visibility and `z` ordering;
- declarative project UI in `ui.json`;
- UI button actions such as `new_game`, `menu`, `continue`, `quit` and `jump:<label>`;
- visual UI Editor with hierarchy, canvas and Inspector;
- UI Editor undo/redo, duplicate, delete, canvas positioning and resize;
- alignment tools and keyboard movement;
- reusable UI hierarchy model with safe reparenting between `Panel` containers;
- clone operations with unique IDs;
- group translation, scaling, alignment and distribution helpers;
- shared multi-selection model;
- Ctrl-click multi-selection in the UI canvas and hierarchy;
- group move, duplicate, delete and reparent operations;
- reusable rectangle-selection geometry helpers;
- visual Scene Editor;
- visual Dialogue Graph Editor;
- graph-to-`.vn` compiler;
- PyInstaller helper and GitHub Actions build matrix.

### Install

```bash
python -m pip install -e .
pytest
```

### Run the demo

```bash
python -m vnengine run examples/demo
# or
pynovel run examples/demo
```

### Open the editor

```bash
pynovel-editor examples/demo
```

The editor contains Script, Scene, Dialogue and UI workflows.

### UI Editor

The UI tab provides a visual canvas for `ui.json`. Create widgets, select one or many from the hierarchy or canvas, edit the active widget in Inspector, move and resize it, duplicate or delete selections, reparent widgets into `Panel` containers, and save.

Group helpers provide translation, scaling, alignment and distribution for editor tooling, while hierarchy operations remain independent of Qt.

Keyboard shortcuts:

- `Ctrl-click`: add/remove a widget from the selection
- `Delete`: delete selected widgets
- `Ctrl+D`: duplicate selection
- `Ctrl+Z`: undo
- `Ctrl+Y`: redo
- `Ctrl+S`: save
- `Arrow keys`: move the selection by 1 pixel
- `Shift + Arrow`: move by 10 pixels

### UI example

```json
{
  "type": "panel",
  "id": "hud",
  "width": "100%",
  "height": "100%",
  "children": [
    {
      "type": "button",
      "id": "start",
      "action": "new_game",
      "x": "50%",
      "y": "50%",
      "width": 240,
      "height": 56,
      "anchor": "center",
      "text": "Start"
    }
  ]
}
```

### UI theme

Put `theme.json` in the project root to customize UI colors.

### Localization

UI catalogs live in `locales/`, for example `ru.json` and `en.json`. Set the project default language in `project.json`; the player profile can override it.

### Script example

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

### Build a standalone game

Build on the target operating system with PyInstaller:

```bash
python -m pip install pyinstaller
python tools/build.py examples/demo --name MyNovel
```

Native bundles are built separately on Windows, macOS and Linux.

---

## Русский

PyNovel Engine — кроссплатформенный движок и редактор визуальных новелл на Python с понятным языком сценариев, визуальным редактированием и переносимым runtime.

### Текущая версия: 0.19.0

### Возможности

- человекочитаемый язык сценариев `.vn`;
- сцены, фоны и персонажи;
- диалоги, повествование и эффект печати;
- выборы мышью и клавиатурой;
- `label`, `jump`, переменные и безопасные выражения;
- `if / else / endif`;
- музыка, звуки, ожидание и переходы;
- выражения персонажей, перемещение и масштабирование с tween-анимацией;
- сохранение и загрузка состояния;
- пять слотов сохранения и постоянный профиль игрока;
- стартовый экран и внутриигровое меню;
- локализация на русском и английском через JSON-каталоги;
- настраиваемая тема через `theme.json`;
- UI-компоненты runtime: `Panel`, `Label`, `Image`, `TextBox`, `Button`;
- anchors, процентные размеры, видимость и `z`-порядок;
- декларативный интерфейс проекта в `ui.json`;
- действия UI-кнопок `new_game`, `menu`, `continue`, `quit` и `jump:<label>`;
- визуальный UI Editor с деревом, canvas и Inspector;
- Undo/Redo, Duplicate, Delete, перемещение и изменение размера;
- безопасный reparenting между контейнерами `Panel`;
- общая модель multi-selection;
- групповой сдвиг, масштабирование, выравнивание и распределение элементов;
- helper геометрии рамки выделения;
- горячие клавиши для работы с группами;
- визуальный Scene Editor;
- визуальный Dialogue Graph Editor;
- компиляция графа в `.vn`;
- сборка через PyInstaller и GitHub Actions.

### Установка

```bash
python -m pip install -e .
pytest
```

### Запуск демо

```bash
python -m vnengine run examples/demo
# или
pynovel run examples/demo
```

### Запуск редактора

```bash
pynovel-editor examples/demo
```

В редакторе есть вкладки **Script**, **Scene**, **Dialogue** и **UI**.

### UI Editor

Во вкладке UI можно визуально собирать `ui.json`: создавать компоненты, выделять один или несколько элементов в дереве или на canvas, менять свойства в Inspector, перемещать, изменять размер, дублировать и удалять элементы, переносить их между контейнерами `Panel` и сохранять результат.

Групповые инструменты поддерживают перемещение, масштабирование, выравнивание и распределение элементов. Основная логика hierarchy и selection не зависит от Qt.

Горячие клавиши:

- `Ctrl-клик`: добавить или убрать виджет из выделения;
- `Delete`: удалить выбранные виджеты;
- `Ctrl+D`: дублировать выделение;
- `Ctrl+Z`: отменить действие;
- `Ctrl+Y`: вернуть действие;
- `Ctrl+S`: сохранить;
- `Стрелки`: перемещение выделения на 1 пиксель;
- `Shift + Стрелки`: перемещение на 10 пикселей.

### Пример UI

```json
{
  "type": "panel",
  "id": "hud",
  "width": "100%",
  "height": "100%",
  "children": [
    {
      "type": "button",
      "id": "start",
      "action": "new_game",
      "x": "50%",
      "y": "50%",
      "width": 240,
      "height": 56,
      "anchor": "center",
      "text": "Начать"
    }
  ]
}
```

### Тема интерфейса

В корень проекта можно положить `theme.json`, чтобы менять оформление без изменения кода движка.

### Локализация

Каталоги интерфейса находятся в `locales/`, например `ru.json` и `en.json`. Язык проекта задаётся в `project.json`, а профиль игрока может хранить пользовательский выбор.

### Сборка

Установите PyInstaller и собирайте игру на целевой ОС:

```bash
python -m pip install pyinstaller
python tools/build.py examples/demo --name MyNovel
```

Нативные сборки создаются отдельно для Windows, macOS и Linux.

### Документация

- [English README](README.md)
- [Полное русское README](README_RU.md)
- [Заметки по упаковке](packaging/README.md)
- [История изменений](CHANGELOG.md)

### Статус проекта

Проект находится в активной разработке. Архитектура разделена на editor, scripting, runtime, rendering, UI и project data, поэтому новые функции добавляются отдельными слоями без переписывания всего движка.
