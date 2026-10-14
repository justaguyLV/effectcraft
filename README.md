# BlockComet Launcher (PojavLauncher build recipe)

This branch holds only a recipe, not Pojav's source. The workflow clones PojavLauncher at a pinned commit,
applies `pojav-custom/apply.sh` (name, yellow accent, icon, first-run copy of bundled game files), adds a Java 17
runtime, Fabric Loader 0.15.11 + Fabric API + Meteor Client 0.5.4 for Minecraft 1.20.1, builds the APK and runs it
once in an emulator.

Minecraft itself is not included: the launcher downloads it from Mojang for an account that owns the game.
PojavLauncher is LGPL-3.0 and Meteor Client is GPL-3.0; this branch is the corresponding source for the changes.
