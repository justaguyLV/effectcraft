# BlockComet on Copper (build recipe)

Holds only a recipe. The workflow clones Copper-Android (MojoLauncher based, LGPL-3.0) at a pinned commit, applies
`copper-custom/apply.sh` (name, yellow Material 3 palette, icons, first-run Meteor instance with Fabric Loader,
Fabric API and Meteor Client 0.5.4 for Minecraft 1.20.1), builds the APK and runs it in an emulator.
Minecraft itself is not included. Meteor Client is GPL-3.0; this branch is the corresponding source for the changes.
