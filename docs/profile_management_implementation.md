# Profile Management

## Objective

Provide GUI-ready profile creation and configuration without manual JSON editing, macro selection, or permanent ROM duplication. A profile associates a prepared battery save with the selected game, starter, trainer name, emulator, macro, and computer vision configuration.

## Implementation

| Component | Responsibility |
|---|---|
| `profiles/game_registry.py` | Central supported-game configuration and starter-to-species mapping. |
| `profiles/profile_manager.py` | Profile naming, metadata generation, save copying, migration, and validation. |
| `instances/library_manager.py` | Load validated profile metadata, resolve ROM paths, dynamically select the macro, and initialize isolated emulator instances. |

The game registry defines FireRed's shared ROM path, mGBA backend, automation macro, vision configuration, and supported starter Pokémon.

### Supported Starter Configuration

| Starter | Species ID |
|---|---|
| Bulbasaur | 001 |
| Charmander | 004 |
| Squirtle | 007 |

ROM paths are relative to the project directory, allowing profiles to remain portable between development computers with matching directory structures.

### Profile Management Functions

| Function | Purpose |
|---|---|
| `generate_profile_name()` | Constructs profile names from game, trainer, and starter selections. |
| `generate_profile_metadata()` | Generates the associated game and hunting configuration. |
| `create_profile()` | Copies the prepared save and creates permanent profile metadata. |
| `migrate_profile()` | Updates existing profile metadata without modifying the battery save. |
| `load_profile()` | Validates metadata against the game registry and verifies required files. |

## Profile Metadata Structure

Example generated profile:

```json
{
    "name": "FireRed ASH Bulbasaur",
    "game": "Pokemon FireRed Rev 1",
    "emulator": "mGBA",
    "rom_path": "roms/Pokemon - FireRed Version (USA, Europe) (Rev 1).gba",
    "save_file": "game.sav",
    "trainer_name": "ASH",
    "target_name": "Bulbasaur",
    "target_species": "001",
    "macro": "macros.firered_main_macro",
    "vision_config": "firered_leafgreen"
}
```

Each permanent profile contains its own battery save and configuration file. Multiple profiles reference a single shared ROM.

```text
saves/
└── FireRed ASH Bulbasaur/
    ├── game.sav
    └── profile.json
```

## Verification

### Game Registry and Profile Generation

All three FireRed starters were tested to verify correct automatic profile generation.

| Verification | Result |
|---|---|
| Supported game selection | PASS |
| ROM path resolution | PASS |
| Starter-to-species mapping | PASS |
| Automatic profile naming | PASS |
| Emulator configuration | PASS |
| Macro configuration | PASS |
| Computer vision configuration | PASS |

### Existing Profile Migration

Three existing profiles were migrated to the expanded metadata structure.

| Profile | Trainer | Target | Species |
|---|---|---|---|
| FireRed Starter | CHRIS | Charmander | 004 |
| FireRed ASH Bulbasaur | ASH | Bulbasaur | 001 |
| FireRed ASH Squirtle | ASH | Squirtle | 007 |

All three permanent battery saves remained byte-for-byte identical following migration.

The original `FireRed Starter` profile name was retained for backward compatibility.

### Profile-Driven Emulator Instances

One automated encounter was executed for each migrated profile to verify that emulator instances could obtain their configuration directly from profile metadata.

| Verification | Bulbasaur | Charmander | Squirtle |
|---|---|---|---|
| Correct species configuration | PASS | PASS | PASS |
| Correct trainer metadata | PASS | PASS | PASS |
| Dynamic macro loading | PASS | PASS | PASS |
| Correct summary screen | PASS | PASS | PASS |
| Temporary instance cleanup | PASS | PASS | PASS |
| Permanent save preservation | PASS | PASS | PASS |

The resulting screenshots were visually inspected to confirm the correct Pokémon summary screen, species, and trainer.

These encounters verified profile-driven configuration and macro execution rather than establishing additional macro reliability statistics.

### Configuration Validation

Valid and invalid profile configurations were tested. Invalid metadata tests were conducted within an isolated temporary directory to avoid modifying permanent profiles.

| Validation Test | Result |
|---|---|
| Existing profile loading | PASS |
| New profile creation | PASS |
| Duplicate profile rejection | PASS |
| Incorrect species ID rejection | PASS |
| Invalid macro rejection | PASS |
| Invalid vision configuration rejection | PASS |
| Unsupported emulator rejection | PASS |
| Invalid ROM path rejection | PASS |
| Unsupported game rejection | PASS |
| Unsupported starter rejection | PASS |
| Missing metadata field rejection | PASS |
| Permanent save preservation | PASS |

## Limitations

- ROM existence and configured paths are verified, but ROM revision identity is not independently validated using file hashes.
- Profile metadata does not establish the player's actual in-game position or trainer name.
- Trainer-name metadata does not automatically modify the trainer name within the game.
- Additional supported games require corresponding registry entries, automation macros, and computer vision configurations.

## Conclusion

The profile management system successfully centralizes game-specific configuration and provides automatic profile generation, migration, and validation.

Emulator instances obtain their automation and computer vision configuration directly from the selected profile. Permanent battery saves remain isolated from temporary emulator instances, allowing profiles to be reused across multiple hunting sessions.