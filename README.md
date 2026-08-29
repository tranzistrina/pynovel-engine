# PyNovel Engine

> Cross-platform, Python-first visual novel engine and editor for Windows, macOS and Linux.
>
> Кроссплатформенный движок и редактор визуальных новелл на Python для Windows, macOS и Linux.

## English

PyNovel Engine is a Python-first visual novel toolkit focused on readable scripting, visual editing and a portable runtime.

### Current version: 0.14.0

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
- UI Editor undo/redo, duplicate and delete;
- UI canvas drag-and-drop positioning;
- resize handle on the selected UI widget;
- alignment tools: Center X, Center Y, Center, Top and Left;
- keyboard movement with arrows and Shift for larger steps;
- keyboard shortcuts: Delete, Ctrl+D, Ctrl+Z, Ctrl+Y, Ctrl+S;
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

The UI tab provides a visual canvas for `ui.json`. Create a widget from the left panel, select it from the hierarchy or canvas, edit its properties in Inspector, then save.

Keyboard shortcuts:

- `Delete`: delete selected widget
- `Ctrl+D`: duplicate
- `Ctrl+Z`: undo
- `Ctrl+Y`: redo
- `Ctrl+S`: save
- `Arrow keys`: move by 1 pixel
- `Shift + Arrow`: move by 10 pixels

The selected widget can be resized by dragging the lower-right handle and aligned with the Inspector tools.

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

### Текущая версия: 0.14.0

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
- действия кнопок `new_game`, `menu`, `continue`, `quit` и `jump:<label>`;
- визуальный UI Editor с деревом, canvas и Inspector;
- Undo/Redo, Duplicate и Delete;
- перемещение виджетов мышью на canvas;
- resize handle у выбранного виджета;
- инструменты выравнивания Center X, Center Y, Center, Top и Left;
- перемещение стрелками с шагом 1 или 10 пикселей;
- горячие клавиши `Delete`, `Ctrl+D`, `Ctrl+Z`, `Ctrl+Y`, `Ctrl+S`;
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

Во вкладке UI можно визуально собирать `ui.json`: создавать виджеты, выбирать их в дереве или на canvas, менять свойства в Inspector и сохранять результат.

Горячие клавиши:

- `Delete`: удалить выбранный виджет;
- `Ctrl+D`: дублировать;
- `Ctrl+Z`: отменить;
- `Ctrl+Y`: вернуть;
- `Ctrl+S`: сохранить;
- `Стрелки`: перемещение на 1 пиксель;
- `Shift + Стрелки`: перемещение на 10 пикселей.

Размер выбранного виджета можно менять перетаскиванием нижнего правого resize handle. В Inspector доступны инструменты выравнивания.

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

Положите `theme.json` в корень проекта, чтобы настраивать оформление без изменения кода движка.

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
