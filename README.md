# PyNovel Engine

> Cross-platform, Python-first visual novel engine and editor for Windows, macOS and Linux.
>
> Кроссплатформенный движок и редактор визуальных новелл на Python для Windows, macOS и Linux.

## English

PyNovel Engine is a Python-first visual novel toolkit with readable scripting, visual scene/dialogue/UI/animation editing, asset management, and a portable runtime.

### Current version: 0.25.0

### Features

- readable `.vn` scripting;
- scenes, backgrounds, characters and expressions;
- dialogue, narration, choices, labels and jumps;
- variables and safe expressions with `if / else / endif`;
- music, sound, waits, transitions and tween animations;
- save/load, history, five slots and persistent player profile;
- title screen, in-game menu and localization;
- runtime UI widgets: `Panel`, `Label`, `Image`, `TextBox`, `Button`;
- anchors, percentage dimensions, visibility and z-order;
- declarative `ui.json` interfaces and button actions;
- visual Scene, Dialogue and UI editors;
- UI hierarchy with safe reparenting and unique-id cloning;
- multi-selection and group transforms;
- box-selection geometry and group bounding-box transforms;
- Asset Catalog with image, audio, video, font, data, script and other resource types;
- persistent `.pynovel/assets.json` project asset index;
- `pynovel assets scan <project>` resource scanning command;
- Asset Browser with search, type filtering, image/text preview and path copy;
- shared asset drag-and-drop protocol;
- dropping image assets into Scene creates character objects;
- dropping image assets into UI creates image widgets;
- animation timeline with tracks, keyframes, easing, play/pause/stop/seek and loop;
- Animation Editor with timeline, tracks, keyframe editing and playhead;
- runtime timeline player for `animation.json`;
- `.vn` commands `play_animation`, `animation` and `stop_animation`;
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

The generated index is stored at `.pynovel/assets.json` and uses normalized project-relative paths. Assets can be dragged from the Asset Browser onto compatible editor canvases.

### Animation timeline

Animations are stored in `animation.json` as tracks containing keyframes. A single timeline can use the compact format:

```json
{
  "name": "AliceEnter",
  "loop": false,
  "tracks": [
    {
      "target": "Alice",
      "property": "x",
      "keys": [
        {"time": 0.0, "value": 0.0, "easing": "ease_out"},
        {"time": 0.6, "value": 50.0, "easing": "ease_in_out"}
      ]
    }
  ]
}
```

Play it from a script with `play_animation AliceEnter`. The aliases `animation AliceEnter` and `stop_animation AliceEnter` are also supported.

### UI editing

- `Ctrl-click`: add/remove a widget from selection;
- `Delete`: delete selected widgets;
- `Ctrl+D`: duplicate;
- `Ctrl+Z` / `Ctrl+Y`: undo / redo;
- `Ctrl+S`: save;
- Arrow keys: move by 1 px;
- Shift + Arrow: move by 10 px.

The editor-side geometry layer provides normalized marquee rectangles, intersection checks, group bounds and proportional group scaling for canvas tools.

### Build

```bash
python -m pip install pyinstaller
python tools/build.py examples/demo --name MyNovel
```

Build native bundles separately on Windows, macOS and Linux.

---

## Русский

PyNovel Engine — кроссплатформенный движок и редактор визуальных новелл на Python с понятным языком сценариев, визуальным редактированием сцен, диалогов, UI и анимаций, управлением ресурсами и переносимым runtime.

### Текущая версия: 0.25.0

### Возможности

- человекочитаемый язык сценариев `.vn`;
- сцены, фоны, персонажи и выражения;
- диалоги, повествование, выборы, `label` и `jump`;
- переменные и безопасные выражения с `if / else / endif`;
- музыка, звуки, ожидания, переходы и tween-анимации;
- сохранение/загрузка, история, пять слотов и профиль игрока;
- Title Screen, игровое меню и локализация;
- UI-компоненты runtime: `Panel`, `Label`, `Image`, `TextBox`, `Button`;
- anchors, процентные размеры, видимость и `z`-порядок;
- декларативный `ui.json` и actions кнопок;
- визуальные редакторы Scene, Dialogue и UI;
- hierarchy UI с безопасным reparenting и уникальными ID;
- multi-selection и групповые трансформации;
- геометрия рамки выделения и bounding box группы;
- Asset Catalog с классификацией изображений, аудио, видео, шрифтов, данных, скриптов и прочих ресурсов;
- постоянный индекс `.pynovel/assets.json`;
- команда `pynovel assets scan <project>`;
- Asset Browser с поиском, фильтрами, предпросмотром и копированием пути;
- общий drag-and-drop протокол ассетов между canvas редактора;
- перетаскивание изображения в Scene автоматически создаёт персонажа;
- перетаскивание изображения в UI автоматически создаёт `Image`;
- animation timeline с tracks, keyframes, easing, play/pause/stop/seek и loop;
- Animation Editor с timeline, tracks, редактированием keyframes и playhead;
- runtime-проигрыватель `animation.json`;
- команды `.vn` `play_animation`, `animation` и `stop_animation`;
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

В редакторе есть рабочие области **Script**, **Scene**, **Dialogue**, **UI**, **Animation** и **Assets**.

### Управление ресурсами

```bash
pynovel assets scan examples/demo
```

Индекс сохраняется в `.pynovel/assets.json`, а пути внутри проекта хранятся в нормализованном относительном виде. Из Asset Browser изображения можно перетаскивать непосредственно на совместимые canvas.

### Анимационная timeline

Анимации хранятся в `animation.json` как набор треков с ключевыми кадрами. Компактный формат одной timeline:

```json
{
  "name": "AliceEnter",
  "loop": false,
  "tracks": [
    {
      "target": "Alice",
      "property": "x",
      "keys": [
        {"time": 0.0, "value": 0.0, "easing": "ease_out"},
        {"time": 0.6, "value": 50.0, "easing": "ease_in_out"}
      ]
    }
  ]
}
```

Запуск из сценария: `play_animation AliceEnter`. Также доступны алиасы `animation AliceEnter` и `stop_animation AliceEnter`.

### UI Editor

- `Ctrl-клик`: добавить/убрать виджет из выделения;
- `Delete`: удалить выбранные виджеты;
- `Ctrl+D`: дублировать;
- `Ctrl+Z` / `Ctrl+Y`: отмена / возврат;
- `Ctrl+S`: сохранить;
- стрелки: перемещение на 1 пиксель;
- `Shift + Стрелки`: перемещение на 10 пикселей.

Editor-слой также содержит переиспользуемую геометрию для marquee selection, проверки пересечений, bounding box группы и пропорционального масштабирования.

### Сборка

```bash
python -m pip install pyinstaller
python tools/build.py examples/demo --name MyNovel
```

Нативные сборки создаются отдельно для Windows, macOS и Linux.

### Документация

- [English](README.md)
- [Русский](README_RU.md)
- [Changelog](CHANGELOG.md)
