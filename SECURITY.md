# Security

**Reporting a vulnerability.** Please do not open a public issue for a security problem. Use GitHub's *Report a vulnerability*
(Security tab) of this repository, or ask for a private channel on the Discord server linked in the README.

**Scope.** The code added by this project: Color Studio, fonts, the look export/import, the About page, build scripts.
Problems in Copper, Pojav, Meteor, Fabric or the mods belong to those projects (tell us too, so we can update).

**Things the project already does.**
* Importing a look reads only known settings with checked values, matches ZIP entries by name (never by a path from the file),
  and limits sizes.
* Mod jars are checked against pinned SHA-256 (Meteor 1.20.1-1.21.1) or the hash published by Modrinth / Fabric's Maven before
  they are bundled.
* Releases are signed; with your own key (see docs/BUILDING.md) only you can publish updates.

**Not covered.** Servers' rules, and what you do with Meteor Client.
