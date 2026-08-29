# PyNovel Engine

> Cross-platform, Python-first visual novel engine and editor for Windows, macOS and Linux.
>
> Кроссплатформенный движок и редактор визуальных новелл на Python для Windows, macOS и Linux.

[Русский раздел ниже](#русский)

## English

PyNovel Engine is a Python-first visual novel toolkit focused on readable scripting, a visual editor and a portable runtime.

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
- in-game menu with Resume, New Game, Save, Load, History, Settings, Main Menu and Quit
- five save slots
- persistent player profile
- title screen
- Russian and English localization through JSON catalogs
- configurable UI theme through `theme.json`
- declarative runtime UI widgets: Panel, Label, Image, TextBox and Button
- percentage sizing, anchors and z-order for UI layouts
- JSON UI documents for project-defined interfaces
- resizable window and fullscreen
- pygame-ce runtime
- PySide6 desktop editor
- visual Scene editor
- visual Dialogue graph editor
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

The editor contains Script, Scene and Dialogue workflows. Scene editing handles visual character placement; Dialogue editing handles branching story graphs and compilation to `game.vn`.

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

Project UI can be described as JSON and loaded with `UIDocument`.

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

Supported widgets: `panel`, `label`, `image`, `textbox`, `button`. Widgets support nesting, anchors, percentage dimensions, visibility and `z` ordering.

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

PyNovel Engine это движок и редактор визуальных новелл с упором на понятный сценарный язык, визуальное редактирование и кроссплатформенный runtime.

### Возможности

- понятный язык сценариев `.vn`
- сцены, фоны и персонажи
- диалоги и повествование с эффектом печати
- выборы мышью и клавиатурой
- `label`, `jump`, переменные и безопасные выражения
- `if / else / endif`
- музыка, звуки, задержки и переходы
- выражения персонажей, перемещение и масштабирование с tween-анимацией
- сохранение и загрузка состояния, включая фон, персонажей и историю
- внутриигровое меню: продолжить, новая игра, сохранить, загрузить, история, настройки, главное меню и выход
- пять слотов сохранения
- постоянный профиль игрока
- стартовый экран
- локализация интерфейса через JSON-каталоги на русском и английском
- настраиваемая тема интерфейса через `theme.json`
- декларативные UI-компоненты runtime: Panel, Label, Image, TextBox и Button
- процентные размеры, anchors и z-порядок UI-компонентов
- JSON-документы для интерфейсов проекта
- изменение размера окна и полноэкранный режим
- runtime на pygame-ce
- редактор на PySide6
- визуальный редактор сцен
- визуальный редактор графа диалогов
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

В редакторе есть рабочие области Script, Scene и Dialogue. В Scene персонажи размещаются визуально, а в Dialogue создаётся ветвящийся граф истории с последующей компиляцией в `game.vn`.

### Управление в игре

- `Enter` / `Space`: продолжить
- `1-9`: выбрать вариант
- `Esc`: открыть внутриигровое меню
- `F5`: быстрое сохранение в слот 1
- `F9`: быстрая загрузка из слота 1
- `F7`: пропуск текста
- `F8`: автоматический режим
- `F11`: полноэкранный режим

### UI-интерфейс

Интерфейс проекта можно описывать через JSON и загружать с помощью `UIDocument`.

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

Поддерживаются `panel`, `label`, `image`, `textbox`, `button`. Компоненты можно вкладывать друг в друга; доступны anchors, процентные размеры, видимость и порядок `z`.

### Тема интерфейса

Положите `theme.json` в корень проекта для настройки цветов интерфейса:

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

### Локализация

Каталоги интерфейса находятся в `locales/`, например `ru.json` и `en.json`. Язык проекта задаётся в `project.json`, а профиль игрока может его переопределить.

### Пример сценария

```text
title "Моя первая новелла"
background "assets/room.png"
character Alice "assets/alice.png" center happy
expression Alice excited
move Alice left 0.45
scale Alice 1.08 0.35
say Alice "Привет."
set affection = 2
set affection += 3
if affection >= 5
say Narrator "Открыта новая ветка!"
else
say Narrator "Продолжай играть."
endif
choice
"Продолжить": next
"Закончить": ending
```

### Сборка готовой игры

Установите PyInstaller и собирайте приложение на целевой ОС:

```bash
python -m pip install pyinstaller
python tools/build.py examples/demo --name MyNovel
```

Готовые нативные сборки создаются отдельно для Windows, macOS и Linux.

### Документация

- [English README](README.md)
- [Полное русское README](README_RU.md)
- [Заметки по упаковке](packaging/README.md)

### Статус проекта

Проект находится в активной разработке. Архитектура разделена на editor, scripting, runtime, rendering, UI и project data, поэтому новые функции добавляются отдельными слоями без переписывания всего движка.
