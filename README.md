# Asperis

Action platformer prototype with combat and a player controller inspired by Hollow Knight, built with Python and Pygame on top of a custom Entity-Component-System architecture.

## Video Showcase
Enemies knock each other apart so a group chasing the player doesn't stack into one pile.
<p align="center" width="100%">
<video src="https://github.com/user-attachments/assets/1541f20e-9c03-4b10-b905-af1c46f573d2" width="80%" controls></video>
</p>

Slashing downward on an enemy while airborne bounces the player back up, as in Hollow Knight. (so called "pogo")
<p align="center" width="100%">
<video src="https://github.com/user-attachments/assets/e8e0ffeb-21db-4789-8d8d-5d58b15d0125" width="80%" controls></video>
</p>

Boss has a charge attack that triggers when player comes within its range. After attacking it has a cooldown so the player has a window to land a hit.
<p align="center" width="100%">
<video src="https://github.com/user-attachments/assets/ecae6fed-efd0-489d-8e42-212ed8c19ae2" width="80%" controls></video>
</p>

## About This Project

This started as a school project where I had to build a simple game in Python, however I wanted to explore architecture and design patterns and use this opportunity to build something cool. I had two main goals with this: build a clean ECS architecture from scratch (entities, components, systems with command and observer pattern) and get a platformer character controller that feels like Hollow Knight with things like: tight air control, coyote time, jump buffering, a dash, and a 4-directional slash attack.

It is intentionally a core/prototype build, not a finished game. There's no art direction, no real level design, and no custom map, the tiles are plain gray rectangles placed directly in code, and enemies/the boss are functional stand-ins for testing combat and AI rather than a designed encounter. The point of the project is the architecture and the controller feel underneath it, not the presentation.

## Features

Architecture:
- Custom ECS: `EntityManager` (component storage + queries), `Component` dataclasses, `System`/`SystemManager` (ordered, individually pausable updates)
- Command pattern for all input-driven actions (movement, jump, dash, attack, pause, scene transitions, quitting)
- Event bus (`EventManager`/`EventListener`) that decouples: screen shake, particle bursts, hit resolution, animation switches, and UI text updates all flow as events
- Scene based flow (`MenuScene` -> `GameScene` -> `GameOverScene`), each with an isolated entity/system world
- `AssetManager` recursively preloads and caches every sprite under `assets/`
- Inspired by the architecture of my other project (also ECS based): https://github.com/docray5/sandbox

Rendering:
- Low-res internal render target (640×360) upscaled 2× to a 1280×720 window for a crisp pixel-art look
- Full animation state machine per character (idle, moving, attack, hit, death)
- Camera with smooth lerp-follow, dead zone, and screen shake
- Particle effects: attack slashes, blood splatter, landing dust, jump puffs, victory/defeat bursts
- Optional debug hitbox overlay (inside `core.py`)

Player controller:
- Acceleration/friction movement with separate ground and air handling
- Coyote time + jump buffering + variable jump height
- Dash with cooldown, limited charges (refills on landing), full 8-directional aim
- 4-directional melee attack with a dynamically repositioned sword hitbox
- Hit invincibility frames with a visual flash, on-screen health bar

Enemies (functional test content for the combat/AI systems, not designed encounters):
- Patrolling - paces a platform, edge-detects so it won't walk off ledges
- Following - chases the player within a sight range and can jump obstacles
- Boss - approach -> attack windup -> attack -> cooldown loop, larger detection/attack range, telegraphed swings
- Enemy-vs-enemy separation knockback, brief post-hit invincibility to prevent stun-locking

Game flow:
- Menu with Play/Quit and on-screen instructions
- Pause overlay (freezes gameplay systems, keeps rendering/UI/particles alive)
- Win (all enemies defeated) and lose (player health depleted) conditions, each with a dedicated Game Over screen and particle burst

## Controls

| Action                                                  | Input                       |
|---------------------------------------------------------|-----------------------------|
| Move left / right                                       | `A` / `D`                   |
| Jump (hold longer for a full jump, tap for a short hop) | `Space`                     |
| Aim attack up / down                                    | `W` / `S`                   |
| Dash                                                    | `Left Ctrl`                 |
| Attack                                                  | `Right Ctrl` or Mouse Click |
| Pause / resume                                          | `Esc`                       |
| Click menu and pause buttons                            | Mouse                       |

## Architecture Notes

- Components are plain data (dataclasses), they have no behavior
- Systems hold all behavior and operate once per frame on entities matching a component query (`entity_manager.get_entities_with(...)`). Systems run in the order they're added to `SystemManager` and can be individually paused (used for the pause menu, which keeps `RenderSystem`, `InputSystem`, and `ClickableSystem` running while freezing everything else).
- Commands turn a raw input event into a call against a system (e.g. `MoveLeftDownCmd` -> `player_system.left_key_down()`), so `InputSystem` never needs to know about game logic directly.
- Events go the other way. When a system causes a side effect (taking damage, landing hard, finishing an attack), it notifies the EventManager, and any subscribed system reacts (camera shake, particle burst, animation swap) without needing a reference back to the source.

## Scope & Known Limitations

As a prototype focused on architecture and controller feel, several things were deliberately left out or left rough:

- No real art or level design. Tiles are plain gray rectangles placed directly in code. The "levels" (`create_level()` / `create_debug_level()` in `scenes.py`) are test layouts, not designed content.
- Placeholder visuals. Colors and simple shapes stand in for a proper art style; the animation system is fully built out, but it's driven by whatever sprite sheets you drop into `assets/`.
- Camera has no bounds clamping yet (`# TODO bounds` in `camera.py`) - it will follow the player past the edges of the level.
- No save/persistence between runs; state resets on scene switch (`core.reinitialize()`).
- Levels are hardcoded rather than loaded from data/tilemap files.
- Single keybind scheme, not remappable at runtime.

## Credits (assets)
- https://jesse-m.itch.io/skeleton-pack
- https://xzany.itch.io/free-knight-2d-pixel-art
- https://zerie.itch.io/tiny-rpg-character-asset-pack
- https://frostwindz.itch.io/pixel-art-slashes