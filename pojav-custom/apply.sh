#!/usr/bin/env bash
# Applies the "BlockComet" customisations to a checkout of PojavLauncher.
#   usage: apply.sh <pojav-dir>
set -euo pipefail
P="$(cd "$1" && pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"
RES="$P/app_pojavlauncher/src/main/res"
JAVA="$P/app_pojavlauncher/src/main/java/net/kdt/pojavlaunch"

# 1. Name
sed -i 's|<string name="app_name">.*</string>|<string name="app_name">BlockComet Launcher</string>|' "$RES/values/strings.xml"
sed -i 's|<string name="app_short_name">.*</string>|<string name="app_short_name">BlockComet</string>|' "$RES/values/strings.xml"
grep -q "BlockComet Launcher" "$RES/values/strings.xml"

# 2. Yellow accent (progress bars, selection lines, scrollbars, the login bar) and icon background
sed -i 's|<color name="minebutton_color">#[0-9A-Fa-f]*</color>|<color name="minebutton_color">#FFC107</color>|' "$RES/values/colors.xml"
sed -i 's|<color name="ic_launcher_background">#[0-9A-Fa-f]*</color>|<color name="ic_launcher_background">#FFC107</color>|' "$RES/values/ic_launcher_background.xml"
grep -q "FFC107" "$RES/values/colors.xml"
grep -q "FFC107" "$RES/values/ic_launcher_background.xml"

# 2b. The PLAY button is a green 9-patch image: shift every greenish pixel to yellow (keeps shading and alpha)
python3 - "$RES/drawable/mine_button_unfocused.9.png" <<'PY'
import sys, colorsys
from PIL import Image
path = sys.argv[1]
im = Image.open(path).convert("RGBA")
px = im.load()
for y in range(im.height):
    for x in range(im.width):
        r, g, b, a = px[x, y]
        if a and g > r and g > b:
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            nr, ng, nb = colorsys.hsv_to_rgb(48 / 360, min(1.0, s * 0.95), v)
            px[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)
im.save(path)
print("button recoloured")
PY

# 3. Icons, from pojav-custom/logo.png
python3 - "$RES" "$HERE/logo.png" <<'PY'
import sys
from PIL import Image, ImageDraw
res, logo_path = sys.argv[1], sys.argv[2]
logo = Image.open(logo_path).convert("RGBA")
legacy = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
for d, px in legacy.items():
    base = logo.resize((px, px), Image.LANCZOS)
    base.save(f"{res}/mipmap-{d}/ic_launcher.png")
    mask = Image.new("L", (px * 4, px * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, px * 4 - 1, px * 4 - 1), fill=255)
    mask = mask.resize((px, px), Image.LANCZOS)
    rnd = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    rnd.paste(base, (0, 0), mask)
    rnd.save(f"{res}/mipmap-{d}/ic_launcher_round.png")
# Adaptive foreground: 108dp canvas, artwork inside the 66dp safe zone
for d, px in {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}.items():
    canvas = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    inner = int(px * 0.60)
    art = logo.resize((inner, inner), Image.LANCZOS)
    canvas.paste(art, ((px - inner) // 2, (px - inner) // 2), art)
    canvas.save(f"{res}/mipmap-{d}/ic_launcher_foreground.png")
print("icons written")
PY

# 4. Copy the bundled Fabric/Meteor files (and the profile) into the game directory on first start
python3 - "$JAVA/tasks/AsyncAssetManager.java" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
anchor = 'Tools.copyAssetFile(ctx,"resolv.conf",Tools.DIR_DATA, false);'
assert anchor in s, "anchor not found: Pojav changed?"
s = s.replace(anchor, anchor + "\n                copyBundledGameFiles(ctx);", 1)
method = '''
    /** BlockComet: drop the bundled Fabric version JSON and mods into the game directory (never overwrites). */
    private static void copyBundledGameFiles(Context ctx) throws IOException {
        android.content.res.AssetManager am = ctx.getAssets();
        String[] mods = am.list("custom/mods");
        if (mods != null) {
            for (String mod : mods) {
                Tools.copyAssetFile(ctx, "custom/mods/" + mod, Tools.DIR_GAME_NEW + "/mods", false);
            }
        }
        String[] versions = am.list("custom/versions");
        if (versions != null) {
            for (String file : versions) {
                String id = file.endsWith(".json") ? file.substring(0, file.length() - 5) : file;
                Tools.copyAssetFile(ctx, "custom/versions/" + file, Tools.DIR_GAME_NEW + "/versions/" + id, false);
            }
        }
    }
'''
marker = "    /** Unpack single files, with no regard to version tracking */"
assert marker in s
s = s.replace(marker, method + "\n" + marker, 1)
open(p, "w", encoding="utf-8").write(s)
print("AsyncAssetManager patched")
PY
echo "apply.sh: done"
