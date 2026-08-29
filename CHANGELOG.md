# Changelog

## 0.26.0

- Added character `rotation` to the shared runtime model.
- Added rotation persistence to save/load state.
- Added timeline support for animated `rotation` values.
- Added runtime rendering of rotated character sprites.
- Added direct `.vn` `rotate <character> <degrees> <duration>` tween command.
- Added regression tests for the rotate parser command and zero-rotation default.
- Updated the main bilingual README for 0.26.0.

## 0.25.0

- Connected animation timelines to the runtime.
- Added runtime `TimelinePlayer` for single or multiple timelines.
- Added `.vn` commands `play_animation`, `animation` and `stop_animation`.
- Applied timeline keyframes to runtime character properties: `x`, `y`, `scale` and `opacity`.
- Added support for compact single-timeline `animation.json` files.
- Added runtime animation regression tests.
- Updated demo script to run the `AliceEnter` timeline.
- Updated the main bilingual README for 0.25.0.

## 0.24.0

- Added multi-track animation timeline model.
- Added keyframes for target properties with configurable easing.
- Added `linear`, `ease_in`, `ease_out`, `ease_in_out` and `smooth` easing.
- Added timeline `play`, `pause`, `stop`, `seek`, looping and sampling.
- Added JSON serialization and restoration for animation timelines.
- Added Animation Editor with track/keyframe lists and playhead controls.
- Added demo `examples/demo/animation.json`.
- Added animation timeline regression tests.
- Added Animation tab to the main editor.
- Updated the main bilingual README for 0.24.0.

## 0.23.0

- Added a shared asset drag-and-drop MIME payload format.
- Made Asset Browser entries draggable.
- Added Scene Editor drops that create image-backed character objects at the drop point.
- Added UI Editor drops that create image widgets at the drop point.
- Added automatic unique names/IDs for dropped assets.
- Added asset drag-and-drop regression tests.
- Updated editor version and bilingual README.

## 0.22.0

- Added the Asset Browser to the main PyNovel Editor.
- Added project asset search and type filtering.
- Added image preview and text/data preview.
- Added asset metadata display and clipboard path copy.
- Added automatic asset index refresh from the browser.
- Fixed Qt clipboard access in the Asset Browser.
- Added Asset Catalog regression tests.
- Updated the project version to 0.22.0.

## 0.21.0

- Added project asset catalog and common resource classification.
- Added image, audio, video, font, data, script and other asset types.
- Added filesystem scanning with normalized project-relative paths.
- Added missing-resource validation API.
- Added persistent `.pynovel/assets.json` asset index generation.
- Added `pynovel assets scan <project>` CLI command.
- Added asset catalog and CLI regression tests.
- Added bilingual asset pipeline documentation.

## 0.20.0

- Added reusable group bounding-box and proportional group scaling geometry.
- Added rectangle intersection helpers for marquee selection workflows.
- Added editor transform regression tests for group scaling and bounds.
- Updated the main bilingual README for 0.20.0.
