# Asset Pipeline

## English

PyNovel Engine includes a lightweight asset catalog for project resources.

Scan a project from the CLI:

```bash
pynovel assets scan examples/demo
```

The command creates `.pynovel/assets.json` and prints counts for images, audio, video, fonts, data and scripts.

The catalog normalizes paths to `/` separators and classifies common extensions. It can also report missing referenced paths through the Python API.

## Русский

PyNovel Engine содержит лёгкий каталог ресурсов проекта.

Сканирование запускается из CLI:

```bash
pynovel assets scan examples/demo
```

Команда создаёт `.pynovel/assets.json` и выводит количество изображений, аудио, видео, шрифтов, данных и сценариев.

Пути нормализуются к `/`, тип ресурса определяется по расширению, а Python API умеет проверять отсутствующие ссылки на файлы.
