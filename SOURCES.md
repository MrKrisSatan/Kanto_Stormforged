# Source pins

Every native cart mod is pinned to an exact GitHub release and SHA-256. The scheduled pin bot only accepts resolver-compatible, Yellow-safe releases.

| Mod | Repository | Version | SHA-256 |
| --- | --- | ---: | --- |
| Kanto Reforged | 1Jamie/Kanto-Reforged | 1.5.3 | `544656e1c94636e5624e36b758b689df6d3ecd77a58590672d654e0b31d17aa3` |
| Weather FX | MrKrisSatan/Weather-fx | 4.31.2 | `2f375d9374e360f7719e125f825e4b6596958e4fab8e1e3bb6df7bea7a9d092c` |
| WX Pokémon / Weather Variants | MrKrisSatan/WXpokes | 1.2.0 | `5b9e59931c41a3ec663d5b04fb83a7e8b3950decefcdb6210edee818134741e7` |
| Ultron | MrKrisSatan/Ultron | 2.86.0 | `ffe536972bfcc914cf9b3965b3f476f6f29b1244ed525f59929f2e5fa2435629` |
| Better Buildings | HydroHomie31415/Better-Buildings | 1.16.0 | `77614f4a42137e2c3f4b5aa26672c7ed6fc4008b5c9337bd9f3e65ed40268cdd` |
| HGSS Visual Overhaul | LucianoNeo/gen1recomp-mods | 1.0.2 | `893689848881460975851c62543ae467f1d2d33876285834616846903b7ce02f` |
| Pokéball Colors | mistermiracle3036/Pokeball-Colors | 0.1.64 | `c7182fb6a1bb1ba43969ae725355e69cdaa3c71e6ea696f26f59e5058896fa76` |
| Too Many Balls | mistermiracle3036/Too-Many-Balls | 0.8.8 | `af89e632eb429f0fe0bfe796bfa6ffb9b4b7f3603e82c331a07675f87db1abc0` |
| Damage Numbers | eduardocalafell/gen1recomp-damage-numbers | 0.4.0 | `9dedaf11810e9699abe84b7307f3ce3b136ae19267f8629103ae8712dbd7837a` |
| Evolve in Battle | ZyranCZ/Evolve-in-Battle | 2.0.3 | `7c50fc3231d062a822c7ec150a7d271f7f4878a45f5011b029c3a41f5cd61a19` |
| Running Shoes | thorkdev/gen1recomp-running-shoes | 0.3.0 | `af194a0fe7859c6d00a64cb6d1e054b08280041bd2060c8139da2db7fcdd1177` |
| Battle Art | absol89/Gen2Recomped-DramaticShapes | 2.0.3 | `d9a5a6e8b2917b1e4b2c3b84eb32ab9e84f82e181b3d305cdca4c8c61ce9afff` |

## Automatic update safety

A newer GitHub release is not automatically considered safe. The updater checks the tagged `manifest.json`, requires the expected mod ID, requires Yellow/Gen1 support, requires a semantic release tag the cart resolver can fetch, and verifies the ZIP SHA-256.

Battle Art is intentionally governed by this rule. Gen2-only releases are ignored even when GitHub marks them newer.
