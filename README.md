# PyNovel Engine

> Cross-platform, Python-first visual novel engine and editor for Windows, macOS and Linux.
>
> Кроссплатформенный движок и редактор визуальных новелл на Python для Windows, macOS и Linux.

[Русский раздел ниже](#русский)

## English

PyNovel Engine is a Python-first visual novel toolkit focused on readable scripting, visual editing, and a portable runtime.

### Current version: 0.13.0

### Current capabilities

- readable `.vn` scripting language
- scenes, backgrounds and characters
- dialogue and narration with typewriter effect
- clickable and keyboard choices
- labels, jumps, variables and safe expressions
- `if / else / endif`
- music, sound, waits and transitions
- character expressions, movement and scaling with tweening
- save/load with background, character state and history
- in-game menu and five save slots
- persistent player profile
- title screen
- Russian and English localization through JSON catalogs
- configurable UI theme through `theme.json`
- runtime UI widgets: Panel, Label, Image, TextBox and Button
- percentage sizing, anchors and z-order
- declarative `ui.json` project interfaces
- clickable UI buttons with actions such as `new_game`, `menu`, `continue`, `quit`, and `jump:<label>`
- visual UI Editor with widget tree, canvas and Inspector
- UI Editor Undo/Redo, Duplicate and Delete
- canvas drag-and-drop positioning
- keyboard shortcuts for UI editing: Delete, Ctrl+D, Ctrl+Z, Ctrl+Y, Ctrl+S
- visual Scene Editor
- visual Dialogue Graph Editor
- graph-to-`.vn` compiler
- parser, expression, scene, graph, UI and animation tests
- PyInstaller helper and GitHub Actions build matrix

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

The editor contains Script, Scene, Dialogue and UI workflows. UI editing lets you create widgets, select them from the hierarchy or canvas, change their properties visually, duplicate/delete them, undo or redo changes, and save the result to `ui.json`.

### Runtime controls

- `Enter` / `Space`: continue
- `1-9`: choose an option
- `Esc`: open the in-game menu
- `F5`: quick save slot 1
- `F9`: quick load slot 1
- `F7`: toggle skip mode
- `F8`: toggle auto mode
- `F11`: toggle fullscreen

### UI layout

Project UI can be described as JSON and edited visually in the UI tab.

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

Supported widgets: `panel`, `label`, `image`, `textbox`, `button`. Widgets support nesting, anchors, percentage dimensions, visibility and `z` ordering. Buttons expose declarative actions, keeping project files free of serialized Python callbacks.

### UI editing shortcuts

- `Delete`: remove the selected widget
- `Ctrl+D`: duplicate the selected widget
- `Ctrl+Z`: undo
- `Ctrl+Y`: redo
- `Ctrl+S`: save `ui.json`

### UI theme

Put `theme.json` in the project root to customize UI colors:

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

### Текущая версия: 0.13.0

### Возможности

- человекочитаемый язык сценариев `.vn`
- сцены, фоны и персонажи
- диалоги и повествование с эффектом печати
- выборы мышью и клавиатурой
- `label`, `jump`, переменные и безопасные выражения
- `if / else / endif`
- музыка, звуки, ожидание и переходы
- выражения персонажей, перемещение и масштабирование с tween-анимацией
- сохранение и загрузка состояния
- пять слотов сохранения
- внутриигровое меню и Title Screen
- постоянный профиль игрока
- локализация интерфейса на русском и английском
- настраиваемая тема через `theme.json`
- UI-компоненты runtime: `Panel`, `Label`, `Image`, `TextBox`, `Button`
- процентные размеры, anchors и `z`-порядок
- интерфейсы проекта в `ui.json`
- кликабельные UI-кнопки с actions `new_game`, `menu`, `continue`, `quit` и `jump:<label>`
- визуальный UI Editor с деревом виджетов, canvas и Inspector
- Undo/Redo, Duplicate и Delete в UI Editor
- перемещение элементов непосредственно на canvas мышью
- горячие клавиши `Delete`, `Ctrl+D`, `Ctrl+Z`, `Ctrl+Y`, `Ctrl+S`
- визуальный Scene Editor
- визуальный Dialogue Graph Editor
- компиляция графа в `.vn`
- тесты parser, expressions, сцен, графов, UI и анимаций
- сборка через PyInstaller и GitHub Actions

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

В редакторе есть вкладки **Script**, **Scene**, **Dialogue** и **UI**. Во вкладке UI можно создавать компоненты, выбирать их в дереве или на canvas, менять свойства визуально, дублировать и удалять элементы, отменять и возвращать изменения и сохранять результат в `ui.json`.

### Управление в игре

- `Enter` / `Space`: продолжить
- `1-9`: выбрать вариант
- `Esc`: открыть меню
- `F5`: быстрое сохранение в слот 1
- `F9`: быстрая загрузка из слота 1
- `F7`: пропуск текста
- `F8`: автоматический режим
- `F11`: полноэкранный режим

### Горячие клавиши UI Editor

- `Delete`: удалить выбранный виджет
- `Ctrl+D`: дублировать выбранный виджет
- `Ctrl+Z`: отменить действие
- `Ctrl+Y`: вернуть действие
- `Ctrl+S`: сохранить `ui.json`

### UI-интерфейс

Интерфейс можно описывать в JSON и редактировать визуально во вкладке UI.

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

Поддерживаются `panel`, `label`, `image`, `textbox`, `button`. Компоненты можно вкладывать; доступны anchors, процентные размеры, видимость и порядок `z`.

### Тема интерфейса

В корень проекта можно положить `theme.json` и изменить оформление UI без изменения кода движка.

### Локализация

Каталоги интерфейса находятся в `locales/`, например `ru.json` и `en.json`. Язык проекта задаётся в `project.json`, а профиль игрока может хранить пользовательский выбор.

### Сборка

Установите PyInstaller и собирайте игру на целевой ОС:

```bash
python -m pip install pyinstaller
python tools/build.py examples/demo --name MyNovel
```

Нативные сборки создаются отдельно для Windows, macOS и Linux.

### Статус проекта

Проект находится в активной разработке. Архитектура разделена на editor, scripting, runtime, rendering, UI и project data, поэтому новые функции добавляются отдельными слоями.

### Документация

- [English README](README.md)
- [Полное русское README](README_RU.md)
- [Заметки по упаковке](packaging/README.md)
