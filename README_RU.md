# PyNovel Engine

Python-first движок визуальных новелл для Windows, macOS и Linux.

## Возможности 0.12

- человекочитаемый язык сценариев `.vn`;
- сцены, фоны и персонажи;
- диалоги и narration с эффектом печати;
- выборы мышью и клавиатурой;
- `label`, `jump`, переменные и безопасные выражения;
- `if / else / endif`;
- музыка, звуки, ожидание и переходы;
- выражения персонажей;
- команды `expression`, `move`, `scale`;
- плавные tween-анимации;
- сохранение и загрузка состояния;
- пять слотов сохранения;
- игровое меню и Title Screen;
- настройки скорости текста, громкости и полноэкранного режима;
- постоянный профиль игрока в `profile.json`;
- русская и английская локализация через JSON-каталоги;
- настраиваемая тема интерфейса через `theme.json`;
- runtime UI: `Panel`, `Label`, `Image`, `TextBox`, `Button`;
- процентные размеры, anchors и `z`-порядок UI;
- UI, описанный декларативно через `ui.json`;
- кликабельные UI-кнопки с декларативными actions;
- визуальный UI Editor в PySide6;
- визуальный Scene Editor;
- визуальный Dialogue Graph Editor;
- сохранение `ui.json`, `scene.json` и `dialogue.json`;
- компиляция графа диалогов в `.vn`;
- тесты для parser, expressions, сцен, графов, UI, профиля и анимаций;
- PyInstaller helper и GitHub Actions matrix.

## Архитектура

```text
Project
  │
  ├── scene.json
  ├── dialogue.json
  ├── ui.json
  ├── game.vn
  └── assets/
       │
       ▼
     Editor
       │
       ├── Script Editor
       ├── Scene Editor
       ├── Dialogue Graph
       └── UI Editor
              │
              ▼
           Project Data
              │
              ▼
           Runtime
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
    Windows  macOS  Linux
```

## Установка

```bash
python -m pip install -e .
pytest
```

## Запуск демо

```bash
python -m vnengine run examples/demo
```

или:

```bash
pynovel run examples/demo
```

## Запуск редактора

```bash
pynovel-editor examples/demo
```

В редакторе есть вкладки **Script**, **Scene**, **Dialogue** и **UI**.

В **Scene** персонажи размещаются визуально. В **Dialogue** история собирается из узлов и связей. В **UI** можно создавать интерфейс из готовых компонентов, менять их координаты, размеры, anchors, текст и `z`-порядок, после чего сохранять всё в `ui.json`.

## UI Editor

Поддерживаются компоненты:

```text
Panel
Label
Image
TextBox
Button
```

Пример `ui.json`:

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

Кнопка может использовать декларативный `action`, например `new_game`, `menu`, `continue`, `quit` или `jump:label`.

## Пример сценария

```text
title "Моя первая новелла"
background "assets/background.png"
character Alice "assets/alice.png" center happy
expression Alice excited
move Alice left 0.45
scale Alice 1.08 0.35
say Alice "Привет!"
set affection = 2
set affection += 3
if affection >= 5
say Narrator "Скрытая ветка открыта!"
else
say Narrator "Продолжай играть."
endif
choice
"Продолжить": next
"Закончить": ending
```

## Управление

| Клавиша | Действие |
|---|---|
| Enter / Space | Продолжить / выбрать первый вариант |
| 1-9 | Выбрать вариант |
| Esc | Открыть меню |
| F5 | Быстрое сохранение, слот 1 |
| F9 | Быстрая загрузка, слот 1 |
| F7 | Skip |
| F8 | Auto |
| F11 | Полноэкранный режим |

## Тема интерфейса

В корень проекта можно положить `theme.json`:

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

## Локализация

Каталоги интерфейса размещаются в `locales/`:

```text
locales/
├── ru.json
└── en.json
```

Язык проекта задаётся через `project.json`, а профиль игрока может хранить пользовательский выбор.

## Сборка готовой игры

PyInstaller нужно запускать непосредственно на целевой ОС:

```bash
python -m pip install pyinstaller
python tools/build.py examples/demo --name MyNovel
```

Для Windows, macOS и Linux используются отдельные нативные сборки.

## Статус проекта

Текущая версия разработки: `0.12.0`.

PyNovel Engine развивается как open-source движок визуальных новелл с двумя уровнями работы: визуальное создание игры для начинающих и Python/API-расширение для продвинутых разработчиков.
