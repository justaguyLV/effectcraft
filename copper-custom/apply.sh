#!/usr/bin/env bash
# Applies the "BlockComet" customisations to a checkout of Copper-Android (MojoLauncher based).
#   usage: apply.sh <copper-dir>
set -euo pipefail
P="$(cd "$1" && pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"
RES="$P/app_mojo/src/main/res"
JAVA="$P/app_mojo/src/main/java/git/artdeell/mojo"

# 1. Name (every locale that defines it)
grep -rl 'name="app_short_name"\|name="app_name"' "$RES" --include=strings.xml --include=values.xml | while read -r f; do
  sed -i 's|\(<string name="app_short_name"[^>]*>\)[^<]*|\1BlockComet|; s|\(<string name="app_name"[^>]*>\)[^<]*|\1BlockComet Launcher|' "$f"
done
grep -q ">BlockComet<" "$RES/values/strings.xml"

# 2. Yellow Material 3 palette (light + dark) and icon background
python3 "$HERE/gen_palette.py" "$RES"
sed -i 's|<color name="ic_launcher_background">#[0-9A-Fa-f]*</color>|<color name="ic_launcher_background">#FFC107</color>|' "$RES/values/ic_launcher_background.xml"
grep -q "FFC107" "$RES/values/ic_launcher_background.xml"
grep -q 'md_primary">#FFC107' "$RES/values/colors.xml"

# 3. Icons (same file names and pixel sizes as the existing ones)
python3 - "$RES" "$HERE/logo.png" <<'PY'
import sys, os
from PIL import Image, ImageDraw
res, logo_path = sys.argv[1], sys.argv[2]
logo = Image.open(logo_path).convert("RGBA")
done = 0
for d in ("mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"):
    folder = f"{res}/mipmap-{d}"
    if not os.path.isdir(folder):
        continue
    for name in os.listdir(folder):
        path = f"{folder}/{name}"
        size = Image.open(path).size
        px = size[0]
        if name.startswith("ic_launcher_foreground"):
            canvas = Image.new("RGBA", size, (0, 0, 0, 0))
            inner = int(px * 0.60)
            art = logo.resize((inner, inner), Image.LANCZOS)
            canvas.paste(art, ((px - inner) // 2, (px - inner) // 2), art)
            out = canvas
        elif name.startswith("ic_launcher_background"):
            out = Image.new("RGBA", size, (255, 193, 7, 255))
        elif name.startswith("ic_launcher_round"):
            base = logo.resize(size, Image.LANCZOS)
            mask = Image.new("L", (px * 4, px * 4), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, px * 4 - 1, px * 4 - 1), fill=255)
            mask = mask.resize(size, Image.LANCZOS)
            out = Image.new("RGBA", size, (0, 0, 0, 0))
            out.paste(base, (0, 0), mask)
        elif name.startswith("ic_launcher"):
            out = logo.resize(size, Image.LANCZOS)
        else:
            continue
        fmt = "WEBP" if name.endswith(".webp") else "PNG"
        out.save(path, fmt, lossless=True) if fmt == "WEBP" else out.save(path, fmt)
        done += 1
print("icons written:", done)
assert done >= 10
PY

# 4. Bundled Fabric version + mods: copied on start, and a Meteor instance is the first-run instance
python3 - "$JAVA/tasks/AsyncAssetManager.java" "$JAVA/instances/Instances.java" <<'PY'
import sys
am_path, inst_path = sys.argv[1], sys.argv[2]

s = open(am_path, encoding="utf-8").read()
a1 = "ProgressLayout.setProgress(ProgressLayout.EXTRACT_SINGLE_FILES, 0);"
a2 = 'Tools.copyAssetFile(ctx,"resolv.conf",Tools.DIR_DATA, false);'
marker = "    /** Unpack single files, with no regard to version tracking */"
for a in (a1, a2, marker):
    assert a in s, "anchor not found in AsyncAssetManager: " + a
s = s.replace(a1, "sBundleContext = ctx.getApplicationContext();\n        " + a1, 1)
s = s.replace(a2, a2 + "\n                installBundled(ctx);", 1)
methods = '''    // ---- BlockComet: bundled Fabric version and mods (assets/custom) ----------------------------
    private static Context sBundleContext;

    /** @return the id of the bundled Fabric version, or null if this build has none */
    public static String getBundledVersionId() {
        if (sBundleContext == null) return null;
        try {
            String[] versions = sBundleContext.getAssets().list("custom/versions");
            if (versions == null || versions.length == 0) return null;
            String file = versions[0];
            return file.endsWith(".json") ? file.substring(0, file.length() - 5) : file;
        } catch (IOException e) {
            return null;
        }
    }

    /** Copy the bundled version JSON into the shared versions directory (never overwrites). */
    private static void installBundledVersion(Context ctx) throws IOException {
        String[] versions = ctx.getAssets().list("custom/versions");
        if (versions == null) return;
        for (String file : versions) {
            String id = file.endsWith(".json") ? file.substring(0, file.length() - 5) : file;
            Tools.copyAssetFile(ctx, "custom/versions/" + file, Tools.DIR_HOME_VERSION + "/" + id, false);
        }
    }

    /** Copy the bundled mods into an instance's mods directory (never overwrites). */
    public static void installBundledMods(git.artdeell.mojo.instances.Instance instance) {
        Context ctx = sBundleContext;
        if (ctx == null || instance == null) return;
        try {
            String[] mods = ctx.getAssets().list("custom/mods");
            if (mods == null) return;
            File dir = new File(instance.getGameDirectory(), "mods");
            for (String mod : mods) {
                Tools.copyAssetFile(ctx, "custom/mods/" + mod, dir.getAbsolutePath(), false);
            }
        } catch (IOException e) {
            Log.e("AsyncAssetManager", "Failed to install bundled mods", e);
        }
    }

    /** On every start: put the bundled version and mods in place, also for instances created earlier. */
    private static void installBundled(Context ctx) throws IOException {
        installBundledVersion(ctx);
        String bundled = getBundledVersionId();
        if (bundled == null) return;
        for (git.artdeell.mojo.instances.Instance instance : git.artdeell.mojo.instances.Instances.loadAllInstances()) {
            if (bundled.equals(instance.versionId)) installBundledMods(instance);
        }
    }

'''
s = s.replace(marker, methods + marker, 1)
open(am_path, "w", encoding="utf-8").write(s)

t = open(inst_path, encoding="utf-8").read()
old = '''    private static void createFirstTimeInstance() throws IOException {
        internalCreateInstance((instance)-> {
            instance.sharedData = true;
            instance.versionId = "1.12.2";
        }, null);
    }'''
new = '''    private static void createFirstTimeInstance() throws IOException {
        final String bundled = git.artdeell.mojo.tasks.AsyncAssetManager.getBundledVersionId();
        Instance created = internalCreateInstance((instance)-> {
            if (bundled != null) {
                instance.name = "Meteor Client 1.20.1";
                instance.sharedData = false;
                instance.versionId = bundled;
            } else {
                instance.sharedData = true;
                instance.versionId = "1.12.2";
            }
        }, null);
        if (bundled != null) git.artdeell.mojo.tasks.AsyncAssetManager.installBundledMods(created);
    }'''
assert old in t, "createFirstTimeInstance not found: Copper changed?"
t = t.replace(old, new, 1)
open(inst_path, "w", encoding="utf-8").write(t)
print("java patched")
PY
echo "apply.sh: done"
