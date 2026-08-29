# PyNovel Engine

Python-first движок визуальных новелл для Windows, macOS и Linux.

## Что уже умеет движок

- человекочитаемый язык сценариев `.vn`;
- сцены, фоны и персонажи;
- диалоги и narration с эффектом печати;
- выборы с клавиатуры и мышью;
- `label` и `jump`;
- переменные и безопасные выражения;
- `if / else / endif`;
- музыка и звуковые эффекты;
- ожидание и переходы;
- выражения персонажей;
- команды `expression`, `move`, `scale`;
- плавные tween-анимации;
- сохранение и загрузка состояния;
- пять слотов сохранения;
- игровое меню;
- главное меню/Title Screen;
- настройки скорости текста и громкости;
- постоянный профиль игрока в `profile.json`;
- локализация интерфейса через JSON-каталоги;
- настраиваемая тема интерфейса через `theme.json`;
- редактор проекта на PySide6;
- визуальный Scene Editor;
- визуальный Dialogue Graph Editor;
- сохранение `scene.json` и `dialogue.json`;
- компиляция графа диалогов в `.vn`;
- тесты и GitHub Actions;
- подготовка к сборке через PyInstaller.

## Архитектура

```text
Project
  │
  ├── scene.json
  ├── dialogue.json
  ├── game.vn
  └── assets/
       │
       ▼
     Editor
       │
       ├── Scene Editor
       └── Dialogue Graph
              │
              ▼
           Compiler
              │
              ▼
           game.vn
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

Редактор содержит вкладки Script, Scene и Dialogue.

В Scene можно размещать персонажей визуально. В Dialogue история собирается из узлов и связей.

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

В корень проекта можно положить `theme.json`.

Пример:

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

Таким образом оформление меню отделено от кода движка.

## Локализация

Каталоги интерфейса размещаются в `locales/`.

Например:

```text
locales/
├── ru.json
└── en.json
```

В `project.json` можно задать язык проекта:

```json
{
  "default_language": "ru"
}
```

## Сборка готовой игры

PyInstaller нужно запускать непосредственно на целевой ОС:

```bash
python -m pip install pyinstaller
python tools/build.py examples/demo --name MyNovel
```

Для Windows, macOS и Linux используются отдельные нативные сборки.

## Статус проекта

Текущая ветка разработки: `0.9.0`.

Цель проекта: сделать удобный open-source движок визуальных новелл, в котором начинающий разработчик может собирать игру визуально, а продвинутый пользователь может расширять её Python-кодом и плагинами.
