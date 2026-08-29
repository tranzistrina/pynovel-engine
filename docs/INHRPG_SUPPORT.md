# inhRPG Engine Support Requirements

> **Status snapshot: PyNovel Engine 0.29.0**
>
> This document is the compatibility roadmap for building `inhRPG` as a separate project on top of PyNovel Engine. A checked item means the engine currently has a reusable primitive for that requirement. It does **not** mean the whole `inhRPG` feature is implemented.
>
> **Implemented reusable primitives:** GameSystem registry, event bus, namespaced state registry, scene stack, logical input map, versioned save envelope, 2D map definition/camera, deterministic weighted pathfinding, map selection model, animation timeline/runtime, declarative UI, asset pipeline, and editor support for Scene/UI/Animation/Assets.
>
> **Still required before the full campaign:** generic script extension commands, complete runtime integration of the new extension state/save/input APIs, dynamic UI bindings, full map surface renderer, deterministic scheduler, richer save metadata, notification/log model, audio channels, mini-game scene API, headless integration harness, debug overlay/state inspector, and the remaining P1/P2 tooling listed below.

## Purpose

`inhRPG` is a game built on top of PyNovel Engine. The game remains a separate repository and must depend on the engine through public APIs only.

The engine already provides the visual-novel foundation: `.vn` scripting, scenes, characters, dialogue, choices, variables, conditional branches, sound/music, transitions, animation timelines, save/load, localization, profile/settings, and declarative UI. The current runtime is centered on a linear VN action stream and therefore needs an extension layer before `inhRPG` can be implemented cleanly.

## Compatibility principle

Do not add `inhRPG` rules to the generic engine runtime as one-off special cases. Add reusable engine primitives and expose them through a documented API. The game repository owns the actual crusade rules, data, story content, balancing, factions, units, map definitions, and mini-games.

## Priority levels

- P0: required before the full game implementation can start safely.
- P1: required for the intended complete campaign.
- P2: important quality-of-life or authoring support.
- P3: optional future expansion.

## P0 — Runtime extension API

### 1. Custom game systems

**Status: 🟢 primitive implemented.**

Add a first-class extension interface for game-specific systems:

```python
class GameSystem(Protocol):
    def update(self, dt: float, state: GameState) -> None: ...
    def handle_event(self, event: object, state: GameState) -> bool: ...
    def serialize(self) -> dict: ...
    def deserialize(self, data: dict) -> None: ...
```

Provide registration and lifecycle hooks without modifying the engine's internal action loop for each game.

Required hooks:

- before action execution;
- after action execution;
- per-frame update;
- input/event dispatch;
- scene enter/exit;
- save/load serialization;
- project startup/shutdown.

### 2. Namespaced game state

**Status: 🟢 registry primitive implemented.**

Add a serializable state registry so projects can own structured state without stuffing dictionaries into `Runtime.state.variables`.

Requirements:

- typed/structured state objects;
- namespaces, e.g. `story`, `strategy`, `factions`, `campaign`, `minigames`;
- dirty-state tracking;
- deterministic serialization;
- versioned migrations for save compatibility.

### 3. Events / commands API

**Status: 🟢 event bus primitive implemented; generic script command family still pending.**

Add a generic event bus or command dispatcher usable by both `.vn` scripts and Python systems.

Required examples:

- `strategy.day_started`
- `strategy.battle_started`
- `strategy.battle_finished`
- `faction.relation_changed`
- `resource.threshold_reached`
- `story.flag_changed`
- `minigame.completed`
- `character.relationship_changed`

The event system must support listeners with explicit ordering and safe removal.

### 4. Script extension commands

**Status: 🟡 pending.**

Extend the `.vn` parser and runtime with generic project commands, without hardcoding `inhRPG` names.

Required command family:

```text
call_system system_name method args...
open_scene scene_name
close_scene scene_name
emit event_name ...
set_state namespace.path expression
```

Preferred alternative: a registration API that lets external projects register commands and parsers.

### 5. Non-linear scene stack / overlays

**Status: 🟢 reusable scene stack primitive implemented; runtime loop integration remains.**

The current runtime is effectively one VN scene with optional UI. Add a scene stack so a strategy map, battle result screen, inventory/modal, and mini-game can temporarily cover the VN scene and return to it without destroying context.

Required scene lifecycle:

- `push_scene`
- `pop_scene`
- `replace_scene`
- `pause_underlying`
- input focus ownership
- transition support between stack layers

## P0 — Strategy presentation

### 6. 2D map surface

**Status: 🟡 data/camera primitives implemented; interactive renderer still pending.**

Add a reusable map widget/surface independent from `inhRPG` data.

Requirements:

- arbitrary-size logical map larger than the viewport;
- camera pan;
- zoom;
- drag/keyboard navigation;
- image/tile background;
- layers;
- clickable nodes and areas;
- markers/icons;
- tooltips;
- selection state;
- path/route visualization;
- fog/hidden overlays;
- optional animation.

The engine should not know what a "province" or "army" is. It should render project-defined map entities.

### 7. Map coordinate model

**Status: 🟢 implemented.**

Provide a stable coordinate abstraction:

- logical map coordinates;
- screen coordinates;
- camera transform;
- hit testing;
- viewport conversion.

### 8. Data-driven map definitions

**Status: 🟢 implemented as generic `MapDefinition` model.**

Add a generic `map.json` or similar project asset format containing:

- map dimensions;
- background layers;
- node definitions;
- polygon/area definitions if used;
- connection definitions;
- optional metadata.

Keep simulation state separate from static map definition data.

## P0 — Save/load infrastructure

### 9. Save schema versioning

**Status: 🟢 versioned envelope primitive implemented; full Runtime integration pending.**

The current save model stores action index, variables, history, background and characters. `inhRPG` requires much more state.

Add:

- save schema version;
- engine version;
- project version;
- named state namespaces;
- serializer registry;
- migration hooks;
- corruption validation;
- optional checksum/integrity data.

### 10. Save metadata

**Status: 🟡 pending.**

Support display metadata for save slots:

- chapter/act;
- play time;
- current date/day;
- current location;
- thumbnail/screenshot path;
- player-facing description.

## P0 — Input and UI

### 11. Abstract input actions

**Status: 🟢 serializable logical `InputMap` primitive implemented; Runtime migration pending.**

The current runtime is hardcoded to keyboard/mouse behavior. Add an action map:

```text
confirm
cancel
pause
camera_pan
camera_zoom
select
multi_select
next_dialogue
fast_forward
save
load
```

Allow keyboard and mouse bindings, with future gamepad support.

### 12. Runtime UI API

**Status: 🟡 declarative widget layer implemented; strategy widgets still pending.**

Keep the existing declarative widgets, but expose:

- dynamic text bindings;
- dynamic visibility;
- dynamic enabled/disabled state;
- progress bars;
- icons;
- image layers;
- scroll containers;
- tabs;
- tooltip/popover;
- context menu;
- draggable panels;
- list/grid views;
- templated repeated rows.

A strategy game cannot be built comfortably from static `Label` and `Button` objects alone. Humans, for reasons that remain unclear, enjoy dashboards.

### 13. Data binding

**Status: 🟡 pending.**

Add generic one-way UI bindings from state paths to widget properties, for example:

```text
strategy.supplies -> label.text
campaign.legitimacy -> progress.value
factions.ecclesiarchy.relation -> label.text
selected_army.name -> panel.visible
```

Bindings should be explicit and safe.

## P1 — Strategy simulation support

### 14. Time scheduler

**Status: 🟡 pending.**

Add a deterministic game clock independent of wall-clock time.

Requirements:

- pause;
- time scale;
- next day/week/month ticks;
- scheduled callbacks;
- event queues;
- deterministic ordering;
- save/load of scheduled events.

### 15. Turn/day advancement API

**Status: 🟡 pending; depends on scheduler.**

Expose a simple simulation loop:

```python
campaign.advance_day()
```

The engine provides the scheduler; `inhRPG` owns the actual campaign rules.

### 16. Pathfinding service

**Status: 🟢 deterministic weighted graph pathfinding implemented.**

Generic 2D graph pathfinding for map nodes.

Required:

- weighted graph;
- blocked connections;
- route cost;
- route reconstruction;
- deterministic results.

`inhRPG` can use this for army movement and supply routes.

### 17. Selection framework

**Status: 🟢 reusable map selection primitive implemented.**

Provide single and multi-selection support for map entities, including hover, selected, focus, and disabled states.

### 18. Notification/log system

**Status: 🟡 pending.**

Reusable presentation model for event notifications:

- title;
- body;
- severity;
- icon;
- timestamp/campaign date;
- click action;
- unread state.

## P1 — Animation and media

### 19. Character visual states

**Status: 🟡 partial.**

Current character model supports image/expression/position/scale/opacity/rotation and timeline animation, but structured multi-sprite state is still pending.

Add optional:

- multiple sprites per character;
- named poses;
- emotion variants;
- animation playback state;
- fade/highlight/dim;
- screen-space offsets;
- sprite layering.

### 20. Transition API

**Status: 🟡 partial.**

Current transition implementation is only a timed dark overlay. Add generic transition types and a clean transition interface:

- fade;
- crossfade;
- wipe;
- slide;
- custom shader/renderer transition hook where supported.

### 21. Audio channels

**Status: 🟡 pending.**

Support named channels for music, ambience, effects, UI and voice instead of one music stream plus generic sounds.

## P1 — Mini-game framework

### 22. Generic mini-game scene API

**Status: 🟡 pending.**

Add a reusable base class:

```python
class MiniGameScene:
    def start(self, context): ...
    def update(self, dt): ...
    def handle_input(self, event): ...
    def draw(self, surface): ...
    def result(self) -> dict: ...
```

The engine must support arbitrary mini-games without knowing their rules.

### 23. Mini-game result contract

**Status: 🟡 pending with mini-game API.**

Results must be serializable and return explicit fields such as:

- success/failure;
- score;
- time_used;
- mistakes;
- custom result payload.

## P1 — Debugging and tooling

### 24. Runtime debug overlay

**Status: 🟡 pending.**

Optional developer overlay showing:

- current scene stack;
- script/action index;
- variables/state namespaces;
- active systems;
- FPS;
- asset errors;
- current camera position;
- save schema version.

### 25. Event trace

**Status: 🟡 pending.**

Record a configurable event/action trace for debugging narrative-to-strategy interactions.

### 26. State inspector

**Status: 🟡 pending.**

Developer-only inspector for structured project state.

### 27. Save-state test fixtures

**Status: 🟡 pending.**

Tools to generate deterministic test saves for regression testing.

## P2 — Editor support

### 28. Strategy Map Editor

**Status: 🟡 pending.**

New editor surface for:

- map background/layers;
- nodes and connections;
- markers;
- areas;
- metadata;
- route previews.

### 29. Event editor

**Status: 🟡 pending.**

Visual authoring of campaign events with conditions, effects, choices and follow-up actions.

### 30. State schema viewer

**Status: 🟡 pending.**

Show registered project state namespaces and current values.

### 31. Mini-game preview/editor hooks

**Status: 🟡 pending.**

Optional plugin mechanism for project-owned mini-game editors.

## P2 — Internationalization

### 32. Dynamic formatting in dialogue and UI

**Status: 🟡 pending.**

Support safe formatting/pluralization/interpolation from state values.

Example:

```text
say Cassia "У нас {strategy.supplies} ящиков провианта."
```

### 33. Localized data tables

**Status: 🟡 pending.**

Allow project data such as faction names, unit names and event text to be localized without duplicating simulation definitions.

## P2 — Testing infrastructure

### 34. Engine integration test harness

**Status: 🟡 pending.**

Add a headless mode or controlled runtime mode that allows tests to advance scripts and systems without opening a visible window.

### 35. Deterministic RNG service

**Status: 🟡 pending.**

Provide a seeded RNG service for gameplay systems and save/load reproducibility.

### 36. Golden-state comparison

**Status: 🟡 pending.**

Allow a test to compare serialized state after a known sequence of inputs/actions.

## P3 — Optional future work

### 37. Input/gamepad abstraction

Standard controller/gamepad actions.

### 38. Accessibility

- text scaling;
- colorblind-friendly presentation hooks;
- reduced motion;
- subtitle preferences;
- input remapping.

### 39. Mod/project extension API

Stable plugin discovery and version compatibility for external gameplay packages.

### 40. Performance profiling API

Named scopes for render, script, simulation, pathfinding and asset loading.

## What `inhRPG` should implement itself

The engine must NOT contain these game-specific rules:

- Adeptus Terra / Imperium lore;
- Cassia, Aemilia, Cardinal or inquisitor biographies;
- crusade rules;
- faction definitions;
- supplies, manpower, ammunition or legitimacy formulas;
- army compositions;
- campaign map content;
- event text;
- campaign branching;
- battle balance;
- murder investigation logic;
- mini-game rules;
- endings.

Those belong to `inhRPG`.

## Recommended implementation order

### Phase 1

1. GameSystem API. **🟢**
2. Namespaced serializable state. **🟢**
3. Event bus. **🟢**
4. Scene stack. **🟢 primitive / 🟡 runtime integration**
5. Input actions. **🟢 primitive / 🟡 runtime migration**
6. Save schema/versioning. **🟢 primitive / 🟡 runtime integration**
7. Dynamic UI binding. **🟡**
8. Deterministic RNG. **🟡**

### Phase 2

9. Map surface. **🟡**
10. Camera/selection/pathfinding. **🟢 primitives**
11. Time scheduler. **🟡**
12. Notifications. **🟡**
13. Audio channels. **🟡**
14. Rich character visual states. **🟡**

### Phase 3

15. Mini-game scene API. **🟡**
16. Headless/integration test harness. **🟡**
17. Debug overlay/state inspector. **🟡**
18. Map editor. **🟡**
19. Campaign event editor. **🟡**

## Definition of done for engine support

The engine is ready for `inhRPG` implementation when the game can:

1. run VN scenes and dialogue;
2. push/pop a strategy-map scene without losing VN context;
3. mutate and save structured campaign state;
4. advance campaign time deterministically;
5. render/select/move entities on a 2D map;
6. emit and consume cross-system events;
7. bind strategic state to UI widgets;
8. launch and return from arbitrary mini-games;
9. restore a complete campaign from a save;
10. run deterministic automated tests over representative campaign states.
