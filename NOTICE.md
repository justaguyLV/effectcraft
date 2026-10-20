# Notices

BlockComet Launcher is free software under the GNU LGPL v3 (see `LICENSE` and `COPYING`). This file lists what it is built
on and what it bundles. The same information, generated from the actual files of each build, ships inside the app
(**About → Licenses**) and with every release as `THIRD_PARTY_NOTICES.txt`; if the two differ, the release file is right.

Minecraft is a trademark of Mojang AB / Microsoft. This project is not affiliated with, endorsed by or sponsored by
Mojang or Microsoft. Minecraft is not part of this project.

## Code the launcher is built from

| Project | License | Source |
|---|---|---|
| Copper Launcher | LGPL-3.0 | https://github.com/CopperLauncher/Copper-Android |
| MojoLauncher (base of Copper) | see its repository | https://github.com/MojoLauncher/MojoLauncher |
| PojavLauncher (base of Mojo) | LGPL-3.0 | https://github.com/PojavLauncherTeam/PojavLauncher |

The BlockComet changes are in the `copper-custom/` folder: scripts that patch Copper at the pinned commit named in
`.github/workflows/copper.yml`, and the Java classes they add. Their license is LGPL-3.0, like the code they modify.

## Bundled mods (as of the build this table was written from)

| Mod | License | Source |
|---|---|---|
| Fabric API | Apache-2.0 | https://github.com/FabricMC/fabric |
| FerriteCore | MIT | https://www.curseforge.com/minecraft/mc-mods/ferritecore-fabric |
| Krypton | LGPL-3.0 | see the mod page |
| Lithium | LGPL-3.0-only | https://github.com/CaffeineMC/lithium-fabric |
| Memory Leak Fix | LGPL-2.1-only | https://github.com/fxmorin/memoryleakfix |
| Meteor Client | GPL-3.0 | https://github.com/MeteorDevelopment/meteor-client |
| ModernFix | LGPL-3.0 | https://github.com/embeddedt/ModernFix |
| Noisium | LGPL-3.0 | https://github.com/Steveplays28/noisium |
| ScalableLux | LGPL-3.0-only | https://github.com/RelativityMC/ScalableLux |

Meteor Client is a utility ("hacked") client; many multiplayer servers forbid it. Mod jars are bundled unmodified.
For Meteor Client 1.20.1 to 1.21.1 the jars come from public archives of the official releases; the repository pins the
SHA-256 of each one in `copper-custom/build-mods.sh` and checks it at build time.

## Fonts

Fetched at build time from https://github.com/google/fonts: Poppins, Tajawal, Almarai, IBM Plex Sans Arabic, Cairo, Amiri,
Noto Kufi Arabic, Lato, Montserrat, Nunito, Quicksand, Rubik, Oswald, Orbitron, Roboto Mono, Press Start 2P, VT323, Silkscreen,
Pacifico and Bebas Neue under the SIL Open Font License 1.1; Ubuntu under the Ubuntu Font Licence 1.0. Font files are not
stored in this repository.
