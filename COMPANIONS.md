# Tracked companion mods

These projects are part of the intended STORMFORGED setup, but their current upstream release tags are not semantic versions, so Gen1Recomp's cart resolver cannot pin them directly. The pin bot still tracks and hashes their latest Yellow-safe releases.

| Mod | Repository | Manifest version | Release tag | SHA-256 |
| --- | --- | ---: | --- | --- |
| Auto Save | Czajo/gen1recomp-autosave | 1.0.1 | `latest` | `af978fa07f49dedb82a988120a044d36e7a1f9a4df10c79b5682e9910735a3e8` |
| Music Replacement Mod | AlucardTheFirstHunter/MusicReplacementMod | 2.0.0 | `stereo` | `a7e5e8cdcc264234cc6d90657b97658599fc74b01f2d9efb6e89f75b63a28b5d` |
| Cry Replacement Mod | AlucardTheFirstHunter/CryReplacementMod | 1.0.0 | `anime` | `b113f01fda41cdc16fc139630a5966e42eeedc0f3865e703baafc4f0f2fc9011` |

Once an upstream publishes the same mod under a normal `vX.Y.Z` or `X.Y.Z` release tag, it can be moved into the native cart list and will then participate in automatic cart updates.
