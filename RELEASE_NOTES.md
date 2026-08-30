# KANTO: STORMFORGED v1.1.0 ⚡🌧️

A Yellow-focused rebuild of the STORMFORGED cart plus automatic upstream maintenance.

## Cart changes

- Replaced Dramaless Shape with Battle Art.
- Removed Wilds of Kanto because Battle Art flags the pairing as risky.
- Removed Modern PC UI because Battle Art flags the pairing as risky.
- Removed Mystery Gift because it is not part of the requested lineup.
- Updated Weather FX to 4.31.2.
- Updated WX Pokémon / Weather Variants to 1.2.0.
- Updated Ultron to 2.86.0.
- Updated Pokéball Colors to 0.1.64.
- Added Too Many Balls 0.8.8.
- Added Damage Numbers 0.4.0.
- Added Evolve in Battle 2.0.3.
- Added Running Shoes 0.3.0.
- Added Yellow-safe Battle Art 2.0.3.

## Automatic upstream updates

A new scheduled GitHub Actions workflow checks all native upstreams every six hours.

It only accepts releases whose tags are cart-resolvable semantic versions, whose tagged manifests have the expected mod IDs, and whose game targeting includes Yellow/Gen1. Archive SHA-256s are verified before the cart is changed.

When native pins change, STORMFORGED automatically bumps its patch version, validates the complete cart with Gen1Recomp's official online cart validator and publishes a new latest release.

Battle Art's newer Gen2-only builds therefore do not replace the Yellow-safe pin.

## Companion tracking

Auto Save, Music Replacement Mod and Cry Replacement Mod are tracked separately because their current upstream GitHub release tags are non-semantic and cannot be represented by the current native cart resolver. Their latest Yellow-safe hashes are maintained in `COMPANIONS.md`.
