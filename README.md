# PyNovel Engine

> Cross-platform, Python-first visual novel engine and editor for Windows, macOS and Linux.
>
> Кроссплатформенный движок и редактор визуальных новелл на Python для Windows, macOS и Linux.

## English

PyNovel Engine is a Python-first visual novel toolkit with readable scripting, visual scene/dialogue/UI editing, asset management, and a portable runtime.

### Current version: 0.22.0

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

The editor contains **Script**, **Scene**, **Dialogue**, **UI**, and **Assets** workflows. The Asset Browser indexes project resources and provides fast search, filtering, preview and path copying.

### Asset pipeline

Scan a project from the command line:

```bash
pynovel assets scan examples/demo
```

The generated index is stored at `.pynovel/assets.json` and uses normalized project-relative paths.

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

PyNovel Engine — кроссплатформенный движок и редактор визуальных новелл на Python с понятным языком сценариев, визуальным редактированием, управлением ресурсами и переносимым runtime.

### Текущая версия: 0.22.0

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

В редакторе есть рабочие области **Script**, **Scene**, **Dialogue**, **UI** и **Assets**. Asset Browser индексирует ресурсы проекта и позволяет быстро искать, фильтровать, просматривать и копировать пути к ним.

### Управление ресурсами

Индексировать ресурсы проекта можно из командной строки:

```bash
pynovel assets scan examples/demo
```

Индекс сохраняется в `.pynovel/assets.json`, а пути внутри проекта хранятся в нормализованном относительном виде.

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
