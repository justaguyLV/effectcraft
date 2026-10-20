# Building BlockComet Launcher

The APK is built on GitHub Actions; nothing needs to be installed on your computer. The workflow
(`.github/workflows/copper.yml`) does the following on a Linux runner:

1. downloads Copper Launcher at the commit named in `COPPER_SHA`, with its submodules;
2. fetches the graphics libraries Copper's own CI builds (LTW and Mesa);
3. downloads the mods for each Minecraft version (`copper-custom/build-mods.sh`) and the fonts (`fetch-fonts.sh`);
4. applies the BlockComet changes (`copper-custom/apply.sh`);
5. builds `:app_mojo:assembleFullDebug` with Gradle, signs the APK, verifies the signature;
6. publishes it as a GitHub release and runs it once in an Android emulator.

## Build your own copy

1. Fork this repository (or create a repository from it) and enable **Actions** in its settings.
2. Push to the `main` branch, or run the workflow manually (**Actions → BlockComet on Copper → Run workflow**).
3. Download `BlockComet.apk` from **Releases** (`copper-latest`, a rolling pre-release).
4. For a version release, create and push a tag: `git tag v1.0.0 && git push origin v1.0.0`. A normal release is published and
   `releases/latest/download/BlockComet.apk` points to it.

The workflow's branch list (`on.push.branches`) names the branches that build; change it if you use another branch name.

## Sign with your own key

Without secrets the APK keeps Copper's public debug key (updates install over each other, but anyone can sign an APK with it).
To use your key, create it once on your computer:

```sh
keytool -genkeypair -keystore release.p12 -storetype PKCS12 -alias blockcomet \
        -keyalg RSA -keysize 2048 -validity 10000
base64 -w0 release.p12        # copy the output
```

Then add two repository secrets (**Settings → Secrets and variables → Actions**):

| Secret | Value |
|---|---|
| `ANDROID_KEYSTORE_BASE64` | the base64 text above |
| `KEYSTORE_PASSWORD` | the keystore password (use the same password for the key) |

Keep `release.p12` somewhere safe. If you lose it you cannot publish updates that install over existing ones.

## Update the Copper version

Change `COPPER_SHA` in the workflow to a newer commit of
[CopperLauncher/Copper-Android](https://github.com/CopperLauncher/Copper-Android). The scripts check their anchors and
fail with a clear message when upstream code they patch has changed; fix the script and build again.

## Add or change a bundled Minecraft version

`copper-custom/build-mods.sh` has the list of pinned Meteor Client builds (version, SHA-256) and tries newer Minecraft versions
from Meteor's own snapshot repository. For each version it also fetches the newest stable Fabric Loader, Fabric API and the
performance mods from Modrinth (hashes checked). A version whose files cannot be completed is skipped, with a warning in the
workflow log.

## Where to change the branding

| What | Where |
|---|---|
| Name | `copper-custom/apply.sh` section 1 |
| Logo | `copper-custom/logo.png` (`docs/logo.png` for the README) |
| Discord link | `copper-custom/apply.sh` section 1b |
| Default colors | `copper-custom/gen_palette.py`, `studio.py` |
| Texts of the About page | `copper-custom/apply.sh` section 8 |

## Reading a failed build

The full log of a run is only available inside GitHub's website. Failing steps also write their last relevant lines as an
error annotation (shown at the top of the run page), so you do not need to open the whole log.
