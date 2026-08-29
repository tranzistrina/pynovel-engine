# Packaging

Build on the target operating system with PyInstaller. Native Python/SDL application bundles should be produced on Windows, macOS and Linux separately.

```bash
python -m pip install -e . pyinstaller
python tools/build.py examples/demo --name MyNovel
```

The bundle is written to `dist/`.
