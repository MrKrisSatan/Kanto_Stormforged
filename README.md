# KANTO: STORMFORGED ⚡🌧️

![KANTO: STORMFORGED cartridge label](label.png)

**Latest release: v1.1.0**

**KANTO: STORMFORGED** is a custom Gen1Recomp cartridge built specifically around **Pokémon Yellow**. It combines Kanto Reforged, dynamic Weather FX, WX Pokémon, Ultron's autonomous robot trainers, modern battle presentation and a curated set of quality-of-life/gameplay mods.

The cart deliberately prioritises **Battle Art** as its presentation layer. Dramaless Shape has been removed. **Wilds of Kanto** and **Modern PC UI** are also excluded because Battle Art's current Gen1Recomp releases flag those combinations as risky.

## Native cart mods

| Mod | Version | Project |
| --- | ---: | --- |
| Kanto Reforged | 1.5.3 | [1Jamie/Kanto-Reforged](https://github.com/1Jamie/Kanto-Reforged) |
| Weather FX | 4.31.2 | [MrKrisSatan/Weather-fx](https://github.com/MrKrisSatan/Weather-fx) |
| WX Pokémon / Weather Variants | 1.2.0 | [MrKrisSatan/WXpokes](https://github.com/MrKrisSatan/WXpokes) |
| Ultron | 2.86.0 | [MrKrisSatan/Ultron](https://github.com/MrKrisSatan/Ultron) |
| Better Buildings | 1.16.0 | [HydroHomie31415/Better-Buildings](https://github.com/HydroHomie31415/Better-Buildings) |
| HGSS Visual Overhaul | 1.0.2 | [LucianoNeo/gen1recomp-mods](https://github.com/LucianoNeo/gen1recomp-mods) |
| Pokéball Colors | 0.1.64 | [mistermiracle3036/Pokeball-Colors](https://github.com/mistermiracle3036/Pokeball-Colors) |
| Too Many Balls | 0.8.8 | [mistermiracle3036/Too-Many-Balls](https://github.com/mistermiracle3036/Too-Many-Balls) |
| Damage Numbers | 0.4.0 | [eduardocalafell/gen1recomp-damage-numbers](https://github.com/eduardocalafell/gen1recomp-damage-numbers) |
| Evolve in Battle | 2.0.3 | [ZyranCZ/Evolve-in-Battle](https://github.com/ZyranCZ/Evolve-in-Battle) |
| Running Shoes | 0.3.0 | [thorkdev/gen1recomp-running-shoes](https://github.com/thorkdev/gen1recomp-running-shoes) |
| Battle Art | 2.0.3 | [absol89/Gen2Recomped-DramaticShapes](https://github.com/absol89/Gen2Recomped-DramaticShapes) |

## Tracked companion mods

Three requested projects currently publish their installable builds under non-semantic GitHub tags. Gen1Recomp's cart resolver can only resolve `vX.Y.Z` / `X.Y.Z` GitHub release tags, so these cannot honestly be embedded as native cart pins yet:

- Auto Save — `Czajo/gen1recomp-autosave`
- Music Replacement Mod — `AlucardTheFirstHunter/MusicReplacementMod`
- Cry Replacement Mod — `AlucardTheFirstHunter/CryReplacementMod`

Their current versions and SHA-256s are tracked in [COMPANIONS.md](COMPANIONS.md). The scheduled updater monitors them too, so they will not disappear into a documentation attic.

## Automatic updates

STORMFORGED checks its upstream projects **every six hours** through GitHub Actions.

The updater does **not** simply grab whatever GitHub calls latest. For every candidate native release it verifies:

1. The release tag is semantic and can actually be resolved by a `.g1rcart`.
2. The tagged `manifest.json` has the expected mod ID.
3. The manifest supports **Pokémon Yellow / Gen1**.
4. The release has one unambiguous ZIP asset.
5. The ZIP has a verifiable SHA-256.

If one or more native pins change, the bot bumps the STORMFORGED patch version, validates the complete cart online using Gen1Recomp's official `cartkit`, commits the new pins and dispatches a fresh GitHub release.

This matters for Battle Art: newer releases that declare themselves Gen2-only are automatically rejected for this Yellow cart even if their version number is higher.

## Installation

1. Download the latest `kanto_stormforged-<version>.g1rcart` from Releases.
2. Open Gen1Recomp and import the cart.
3. Let Gen1Recomp download and verify the pinned native mods.
4. Install any currently listed companion mods from their upstream releases.
5. Fully restart Gen1Recomp.
6. Start or load Pokémon Yellow.

The cart targets Gen1Recomp `>=0.1.86 <1.0.0` and allows normal 1× and 2× game speeds.

## Load order

1. Kanto Reforged
2. Weather FX
3. WX Pokémon
4. Ultron
5. Better Buildings
6. HGSS Visual Overhaul
7. Pokéball Colors
8. Too Many Balls
9. Damage Numbers
10. Evolve in Battle
11. Running Shoes
12. Battle Art

Battle Art is last so it owns the final presentation/render layer.

## Removed from the earlier cart

- Dramaless Shape — replaced by Battle Art.
- Wilds of Kanto — removed because Battle Art flags the pairing as risky.
- Modern PC UI — removed because Battle Art flags the pairing as risky.
- Mystery Gift — not part of the requested Stormforged lineup.

## Cartridge identity

- **Base:** Pokémon Yellow
- **Cart ID:** `kanto_stormforged`
- **Version:** 1.1.0
- **Shell:** storm blue `#203746`
- **Finish:** holo
- **Seal:** open

## Credits

STORMFORGED is a curated custom cart. Every included mod remains the work of its respective author and is downloaded from that author's public GitHub releases. The cart pins exact upstream builds rather than repackaging their code.

The result is a tiny thunderstorm of manifests, robots, weather and aggressively modern Poké Balls. ⚡
