# Changelog

## 0.37.0

- Completed the deterministic scheduler increment for campaign simulation support.
- Added absolute-tick scheduling and cancellation for queued events.
- Preserved fractional progress under non-integer time scales instead of silently truncating it.
- Added a derived campaign day from the deterministic tick clock.
- Persisted fractional scheduler progress through save/load serialization.
- Added regression coverage for time scaling, ordering, cancellation, pause/restore, and invalid past scheduling.
- Kept scheduler behavior generic so external projects such as `inhRPG` own their campaign rules.

## 0.36.0

- Routed generic VN extension actions through the public `CommandRegistry` so external projects can register new script commands without modifying the engine action loop.
- Added `command_names()` for introspection of registered project commands.
- Preserved built-in extension commands as engine-owned behavior while allowing arbitrary project-defined commands.
- Added regression coverage proving a registered command executes from a parsed-style action and cannot override built-in extension commands.
- Kept `inhRPG` gameplay rules outside the engine and exposed the capability through reusable public APIs.

## 0.35.0

- Added dynamic UI `enabled` state to reusable widgets.
- Integrated state-to-widget bindings into the main game loop so declarative UI updates from runtime state every frame.
- Added regression coverage for text, visibility and enabled property bindings.
- Kept bindings generic and project-defined, with no `inhRPG`-specific rules in the engine.

## 0.34.0

- Integrated the reusable logical `InputMap` into `ExtensibleRuntime` input dispatch.
- Added public runtime input-handler registration and removal APIs.
- Emitted `input.action` events for logical input actions before handlers run.
- Persisted logical input bindings inside versioned save bundles.
- Added regression coverage for runtime input dispatch and save/load restoration.
- Kept project-specific gameplay rules outside the engine extension layer.

## 0.33.0

- Added reusable extension runtime primitives for systems, state, events, scenes, scheduler, RNG and movement integration.

## 0.28.0

- Added a QGraphics-based animation preview canvas.
- Loaded project `scene.json` characters into the Animation Editor preview.
- Applied timeline `x`, `y`, `scale`, `opacity`, and `rotation` values to preview sprites.
- Connected the live canvas preview to playhead seek and playback.
- Added graphical animation preview regression coverage.
- Updated the main bilingual README for 0.28.0.
