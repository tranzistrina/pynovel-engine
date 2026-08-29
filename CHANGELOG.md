# Changelog

## 0.18.0

- Added a reusable rectangle-selection geometry helper for editor tooling.
- Added normalized box-selection rectangles and intersection tests.
- Added regression tests for rectangle selection behavior.
- Added the `vnengine.editor` package namespace for editor-side reusable models.

## 0.17.0

- Connected the shared multi-selection model to the visual UI Editor.
- Added Ctrl-click multi-selection on the canvas and in the hierarchy tree.
- Added group move, duplicate and delete behavior.
- Added multi-widget reparenting into a target `Panel` container.
- Added group z-order assignment through the UI Editor.
- Kept hierarchy operations independent from Qt through reusable Python helpers.
- Updated the main bilingual README for 0.17.0.

## 0.16.0

- Added a reusable shared selection model for editor tooling.
- Added selection set/add/remove/toggle/clear operations.
- Added group translation and sequential z-order helpers to editor-facing APIs.
- Added regression tests for selection behavior.

## 0.15.0

- Added a reusable UI hierarchy model for editor-side project data.
- Added safe reparenting between `Panel` containers.
- Added cycle prevention when reparenting hierarchy nodes.
- Added cloning helpers with unique IDs.
- Added group translation and sequential z-order helpers.
- Added regression tests for hierarchy operations.
- Updated the main bilingual README for 0.15.0.

## 0.14.0

- Added UI resize handle for the selected widget in the visual UI Editor.
- Added UI alignment actions: Center X, Center Y, Center, Top and Left.
- Added one-pixel keyboard movement with Shift+Arrow ten-pixel movement.
- Improved canvas selection and Inspector synchronization.
- Updated the main bilingual README for 0.14.0.

## 0.13.0

- Added UI Editor undo/redo.
- Added widget duplication and deletion.
- Added canvas drag-and-drop positioning.
- Added UI Editor keyboard shortcuts.

## 0.12.0

- Added the visual UI Editor tab.
- Added widget hierarchy, canvas and Inspector.
- Added UI JSON editing and persistence.

## 0.11.0

- Connected project UI documents to runtime.
- Added declarative button actions.
- Added runtime UI click handling.

## 0.10.0

- Added runtime UI widget primitives.
- Added Panel, Label, Image, TextBox and Button.
- Added anchors, percentage sizing and z ordering.
