# Source pins

Every native cart mod is pinned to an exact GitHub release and SHA-256. The scheduled pin bot only accepts resolver-compatible, Yellow-safe releases.

| Mod | Repository | Version | SHA-256 |
| --- | --- | ---: | --- |
| Kanto Reforged | 1Jamie/Kanto-Reforged | 1.6.2 | `a5c36d33a0549997417643ad317446f35fc7c46e6c14c82067113d717841679e` |
| Weather FX | MrKrisSatan/Weather-fx | 4.35.32 | `cdb2e6ee0725cfe235327e2df8db4c78052ad42d9b49f13c8228b51c40c72424` |
| WX Pokémon / Weather Variants | MrKrisSatan/WXpokes | 1.2.1 | `40da996dc208b3db83a5737faaeb43965ce81ab0e08c634a95ee888cf1d863e8` |
| Ultron | MrKrisSatan/Ultron | 2.1.1 | `bddf75353eade495b5f1998b7b319bd1b66070834f856da70bf3061130d8ffad` |
| Better Buildings | HydroHomie31415/Better-Buildings | 1.16.0 | `77614f4a42137e2c3f4b5aa26672c7ed6fc4008b5c9337bd9f3e65ed40268cdd` |
| HGSS Visual Overhaul | LucianoNeo/gen1recomp-mods | 1.0.3 | `4615d77a0731916f4f828d8a87dbb15fbe5387e7a5b34154000651e68332d2de` |
| Pokéball Colors | mistermiracle3036/Pokeball-Colors | 0.1.64 | `c7182fb6a1bb1ba43969ae725355e69cdaa3c71e6ea696f26f59e5058896fa76` |
| Too Many Balls | mistermiracle3036/Too-Many-Balls | 0.8.8 | `af89e632eb429f0fe0bfe796bfa6ffb9b4b7f3603e82c331a07675f87db1abc0` |
| Damage Numbers | eduardocalafell/gen1recomp-damage-numbers | 0.4.0 | `9dedaf11810e9699abe84b7307f3ce3b136ae19267f8629103ae8712dbd7837a` |
| Evolve in Battle | ZyranCZ/Evolve-in-Battle | 2.0.3 | `7c50fc3231d062a822c7ec150a7d271f7f4878a45f5011b029c3a41f5cd61a19` |
| Running Shoes | thorkdev/gen1recomp-running-shoes | 0.3.0 | `af194a0fe7859c6d00a64cb6d1e054b08280041bd2060c8139da2db7fcdd1177` |
| Battle Art | absol89/Gen2Recomped-DramaticShapes | 2.0.5 | `f610cedcdb5560ae9e6919f01d5e5294fb1865d8f4691468a4545b849c3745ea` |

## Automatic update safety

A newer release is accepted only when its tag is semantic, its manifest ID matches, its manifest targets Yellow/Gen1, and its ZIP hash is verified.
Battle Art prereleases may be examined, but Gen2-only manifests are rejected.
