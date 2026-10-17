#!/usr/bin/env bash
# Applies the "BlockComet" customisations to a checkout of Copper-Android (MojoLauncher based).
#   usage: apply.sh <copper-dir>
set -euo pipefail
P="$(cd "$1" && pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"
RES="$P/app_mojo/src/main/res"
JAVA="$P/app_mojo/src/main/java/git/artdeell/mojo"
MANIFEST="$P/app_mojo/src/main/AndroidManifest.xml"

# 1. Name: "Copper" -> "BlockComet" in the visible texts (not in links), in every locale
python3 - "$RES" <<'PY'
import sys, re, glob
n = 0
for path in glob.glob(sys.argv[1] + "/values*/strings.xml"):
    out = []
    for line in open(path, encoding="utf-8").read().split("\n"):
        if "<string" in line and "http" not in line and "Copper" in line:
            line = re.sub(r"\bCopper\b(?!Launcher)", "BlockComet", line)
            n += 1
        out.append(line)
    open(path, "w", encoding="utf-8").write("\n".join(out))
print("strings rebranded:", n)
PY
sed -i 's|\(<string name="app_short_name"[^>]*>\)[^<]*|\1BlockComet|' "$RES/values/strings.xml"
grep -q ">BlockComet<" "$RES/values/strings.xml"

# 1b. Community link
sed -i 's|\(<string name="social_media_invite"[^>]*>\)[^<]*|\1https://discord.gg/5fhcfW2Ge|' "$RES/values/strings.xml"
grep -q "discord.gg/5fhcfW2Ge" "$RES/values/strings.xml"

# 2. Blue/white Material 3 palette (light + dark) and icon background
python3 "$HERE/gen_palette.py" "$RES"
sed -i 's|<color name="ic_launcher_background">#[0-9A-Fa-f]*</color>|<color name="ic_launcher_background">#1E88E5</color>|' "$RES/values/ic_launcher_background.xml"
grep -q "1E88E5" "$RES/values/ic_launcher_background.xml"
grep -q 'md_primary">#1E88E5' "$RES/values/colors.xml"

# 2b. Defaults: the app's own palette (not the wallpaper colours) and the light (white) mode; both stay selectable in Settings
sed -i 's|PREF_COLOR_SOURCE, SOURCE_DYNAMIC|PREF_COLOR_SOURCE, SOURCE_DEFAULT|' "$JAVA/utils/ThemeManager.java"
sed -i 's|getString(PREF_THEME_MODE, "system")|getString(PREF_THEME_MODE, "light")|' "$JAVA/utils/ThemeManager.java"
python3 - "$RES/xml/pref_appearance.xml" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s2 = s.replace('android:defaultValue="system"\n            android:key="theme_mode"', 'android:defaultValue="light"\n            android:key="theme_mode"', 1)
s2 = s2.replace('android:defaultValue="dynamic"\n            android:key="color_source"', 'android:defaultValue="default"\n            android:key="color_source"', 1)
assert s2 != s, "preference defaults not found"
open(p, "w", encoding="utf-8").write(s2)
PY
grep -q "SOURCE_DEFAULT" "$JAVA/utils/ThemeManager.java"
grep -q '"light")' "$JAVA/utils/ThemeManager.java"

# 3. Look of the menus: much rounder shapes and a different typeface (the font files are fetched by the workflow)
cat > "$RES/values/blockcomet_style.xml" <<'XML'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="ShapeAppearance.BlockComet.Small" parent="ShapeAppearance.Material3.SmallComponent">
        <item name="cornerFamily">rounded</item>
        <item name="cornerSize">16dp</item>
    </style>
    <style name="ShapeAppearance.BlockComet.Medium" parent="ShapeAppearance.Material3.MediumComponent">
        <item name="cornerFamily">rounded</item>
        <item name="cornerSize">24dp</item>
    </style>
    <style name="ShapeAppearance.BlockComet.Large" parent="ShapeAppearance.Material3.LargeComponent">
        <item name="cornerFamily">rounded</item>
        <item name="cornerSize">32dp</item>
    </style>
</resources>
XML
FONTS="$RES/font"
if [ -s "$FONTS/poppins_regular.ttf" ] && [ -s "$FONTS/poppins_medium.ttf" ] && [ -s "$FONTS/poppins_bold.ttf" ]; then
  cat > "$FONTS/blockcomet_sans.xml" <<'XML'
<?xml version="1.0" encoding="utf-8"?>
<font-family xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">
    <font android:fontStyle="normal" android:fontWeight="400" android:font="@font/poppins_regular"
        app:fontStyle="normal" app:fontWeight="400" app:font="@font/poppins_regular" />
    <font android:fontStyle="normal" android:fontWeight="500" android:font="@font/poppins_medium"
        app:fontStyle="normal" app:fontWeight="500" app:font="@font/poppins_medium" />
    <font android:fontStyle="normal" android:fontWeight="700" android:font="@font/poppins_bold"
        app:fontStyle="normal" app:fontWeight="700" app:font="@font/poppins_bold" />
</font-family>
XML
  FONT_ITEMS='        <item name="android:fontFamily">@font/blockcomet_sans</item>
        <item name="fontFamily">@font/blockcomet_sans</item>'
else
  echo "font files missing: keeping the default typeface"
  FONT_ITEMS=''
fi
python3 - "$RES/values/themes.xml" "$FONT_ITEMS" <<'PY'
import sys
p, fonts = sys.argv[1], sys.argv[2]
s = open(p, encoding="utf-8").read()
anchor = '        <item name="windowNoTitle">true</item>'
assert anchor in s, "theme anchor not found"
block = '''        <!-- BlockComet look -->
        <item name="shapeAppearanceSmallComponent">@style/ShapeAppearance.BlockComet.Small</item>
        <item name="shapeAppearanceMediumComponent">@style/ShapeAppearance.BlockComet.Medium</item>
        <item name="shapeAppearanceLargeComponent">@style/ShapeAppearance.BlockComet.Large</item>
''' + (fonts + "\n" if fonts else "") + "\n"
s = s.replace(anchor, block + anchor, 1)
open(p, "w", encoding="utf-8").write(s)
print("theme patched")
PY

# 4. Language option (all translations the app ships), applied with AppCompat's per-app locales
cat > "$RES/values/blockcomet_lang.xml" <<'XML'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="blockcomet_language_title" translatable="false">Language / اللغة</string>
    <string-array name="blockcomet_language_names" translatable="false">
        <item>System default / لغة النظام</item>
        <item>العربية</item><item>English</item><item>English (UK)</item><item>Afrikaans</item><item>Azərbaycanca</item>
        <item>Башҡортса</item><item>বাংলা</item><item>Català</item><item>Čeština</item><item>Dansk</item><item>Deutsch</item>
        <item>Ελληνικά</item><item>Español</item><item>Eesti</item><item>فارسی</item><item>Suomi</item><item>Filipino</item>
        <item>Français</item><item>हिन्दी</item><item>Magyar</item><item>Bahasa Indonesia</item><item>Italiano</item>
        <item>עברית</item><item>日本語</item><item>Қазақша</item><item>한국어</item><item>Lietuvių</item><item>Монгол</item>
        <item>Bahasa Melayu</item><item>Nederlands</item><item>Norsk</item><item>Polski</item><item>Português</item>
        <item>Português (Brasil)</item><item>Română</item><item>Русский</item><item>Slovenčina</item><item>Српски</item>
        <item>Svenska</item><item>ไทย</item><item>Türkçe</item><item>Татарча</item><item>Українська</item>
        <item>Tiếng Việt</item><item>简体中文</item><item>繁體中文</item>
    </string-array>
    <string-array name="blockcomet_language_tags" translatable="false">
        <item></item>
        <item>ar</item><item>en</item><item>en-GB</item><item>af</item><item>az</item>
        <item>ba</item><item>bn</item><item>ca</item><item>cs</item><item>da</item><item>de</item>
        <item>el</item><item>es</item><item>et</item><item>fa</item><item>fi</item><item>fil</item>
        <item>fr</item><item>hi</item><item>hu</item><item>id</item><item>it</item>
        <item>he</item><item>ja</item><item>kk</item><item>ko</item><item>lt</item><item>mn</item>
        <item>ms</item><item>nl</item><item>no</item><item>pl</item><item>pt</item>
        <item>pt-BR</item><item>ro</item><item>ru</item><item>sk</item><item>sr</item>
        <item>sv</item><item>th</item><item>tr</item><item>tt</item><item>uk</item>
        <item>vi</item><item>zh-CN</item><item>zh-TW</item>
    </string-array>
</resources>
XML
python3 - "$RES/xml/pref_appearance.xml" "$JAVA/prefs/screens/LauncherPreferenceAppearanceFragment.java" "$MANIFEST" <<'PY'
import sys
xml_p, java_p, man_p = sys.argv[1:4]
x = open(xml_p, encoding="utf-8").read()
cat = '<PreferenceCategory android:title="@string/preference_category_theme">'
assert cat in x, "theme category not found"
pref = '''
        <androidx.preference.ListPreference
            android:defaultValue=""
            android:key="app_language"
            android:entries="@array/blockcomet_language_names"
            android:entryValues="@array/blockcomet_language_tags"
            android:title="@string/blockcomet_language_title"
            app:iconSpaceReserved="false"
            app:useSimpleSummaryProvider="true" />'''
x = x.replace(cat, cat + pref, 1)
open(xml_p, "w", encoding="utf-8").write(x)

j = open(java_p, encoding="utf-8").read()
anchor = "addPreferencesFromResource(R.xml.pref_appearance);"
assert anchor in j, "appearance anchor not found"
hook = anchor + '''
        androidx.preference.Preference blockCometLanguage = findPreference("app_language");
        if (blockCometLanguage != null) {
            blockCometLanguage.setOnPreferenceChangeListener((preference, newValue) -> {
                String tag = String.valueOf(newValue);
                androidx.appcompat.app.AppCompatDelegate.setApplicationLocales(tag.isEmpty()
                        ? androidx.core.os.LocaleListCompat.getEmptyLocaleList()
                        : androidx.core.os.LocaleListCompat.forLanguageTags(tag));
                return true;
            });
        }'''
j = j.replace(anchor, hook, 1)
open(java_p, "w", encoding="utf-8").write(j)

m = open(man_p, encoding="utf-8").read()
svc = '''        <service
            android:name="androidx.appcompat.app.AppLocalesMetadataHolderService"
            android:enabled="false"
            android:exported="false">
            <meta-data
                android:name="autoStoreLocales"
                android:value="true" />
        </service>
'''
if "AppLocalesMetadataHolderService" not in m:
    assert "</application>" in m
    m = m.replace("</application>", svc + "    </application>", 1)
open(man_p, "w", encoding="utf-8").write(m)
print("language option added")
PY

# 5. Icons (same file names and pixel sizes as the existing ones)
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
            out = Image.new("RGBA", size, (30, 136, 229, 255))
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

# 6. Bundled Fabric versions + mods -> one "Meteor <version>" instance per bundled version
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
methods = '''    // ---- BlockComet: bundled Fabric versions and mods (assets/custom) ---------------------------
    private static Context sBundleContext;

    /** @return ids of the bundled Fabric versions (e.g. fabric-loader-0.19.5-1.20.1); empty if this build has none */
    public static java.util.List<String> getBundledVersionIds() {
        java.util.List<String> ids = new java.util.ArrayList<>();
        if (sBundleContext == null) return ids;
        try {
            String[] versions = sBundleContext.getAssets().list("custom/versions");
            if (versions == null) return ids;
            for (String file : versions) ids.add(file.endsWith(".json") ? file.substring(0, file.length() - 5) : file);
        } catch (IOException ignored) {}
        return ids;
    }

    /** "fabric-loader-0.19.5-1.20.1" -> "1.20.1" */
    public static String gameOf(String versionId) {
        int i = versionId.lastIndexOf('-');
        return i < 0 ? versionId : versionId.substring(i + 1);
    }

    public static android.content.SharedPreferences getBundlePrefs() {
        return sBundleContext.getSharedPreferences("blockcomet", Context.MODE_PRIVATE);
    }

    /** Copy the bundled version JSONs into the shared versions directory (never overwrites). */
    private static void installBundledVersions(Context ctx) throws IOException {
        String[] versions = ctx.getAssets().list("custom/versions");
        if (versions == null) return;
        for (String file : versions) {
            String id = file.endsWith(".json") ? file.substring(0, file.length() - 5) : file;
            Tools.copyAssetFile(ctx, "custom/versions/" + file, Tools.DIR_HOME_VERSION + "/" + id, false);
        }
    }

    /** Copy the bundled mods of the instance's game version into its mods directory (never overwrites). */
    public static void installBundledMods(git.artdeell.mojo.instances.Instance instance) {
        Context ctx = sBundleContext;
        if (ctx == null || instance == null || instance.versionId == null) return;
        try {
            String folder = "custom/mods/" + gameOf(instance.versionId);
            String[] mods = ctx.getAssets().list(folder);
            if (mods == null) return;
            File dir = new File(instance.getGameDirectory(), "mods");
            for (String mod : mods) {
                Tools.copyAssetFile(ctx, folder + "/" + mod, dir.getAbsolutePath(), false);
            }
        } catch (IOException e) {
            Log.e("AsyncAssetManager", "Failed to install bundled mods", e);
        }
    }

    /** On every start: versions in place, an instance for each bundled version (once), mods in place. */
    private static void installBundled(Context ctx) throws IOException {
        installBundledVersions(ctx);
        java.util.List<String> bundled = getBundledVersionIds();
        if (bundled.isEmpty()) return;
        git.artdeell.mojo.instances.Instances.ensureBundledInstances();
        for (git.artdeell.mojo.instances.Instance instance : git.artdeell.mojo.instances.Instances.loadAllInstances()) {
            if (bundled.contains(instance.versionId)) installBundledMods(instance);
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
        if (!git.artdeell.mojo.tasks.AsyncAssetManager.getBundledVersionIds().isEmpty()) {
            ensureBundledInstances();
            return;
        }
        internalCreateInstance((instance)-> {
            instance.sharedData = true;
            instance.versionId = "1.12.2";
        }, null);
    }

    /** BlockComet: creates one "Meteor <game version>" instance for every bundled Fabric version, once per version. */
    public static void ensureBundledInstances() throws IOException {
        java.util.List<String> ids = git.artdeell.mojo.tasks.AsyncAssetManager.getBundledVersionIds();
        if (ids.isEmpty()) return;
        android.content.SharedPreferences prefs = git.artdeell.mojo.tasks.AsyncAssetManager.getBundlePrefs();
        java.util.Set<String> have = new java.util.HashSet<>();
        for (Instance existing : loadAllInstances()) have.add(existing.versionId);
        for (String id : ids) {
            String key = "created_" + id;
            if (have.contains(id) || prefs.getBoolean(key, false)) continue;
            final String versionId = id;
            final String name = "Meteor " + git.artdeell.mojo.tasks.AsyncAssetManager.gameOf(id);
            Instance created = internalCreateInstance((instance)-> {
                instance.name = name;
                instance.sharedData = false;
                instance.versionId = versionId;
            }, null);
            prefs.edit().putBoolean(key, true).apply();
            git.artdeell.mojo.tasks.AsyncAssetManager.installBundledMods(created);
        }
    }'''
assert old in t, "createFirstTimeInstance not found: Copper changed?"
t = t.replace(old, new, 1)
open(inst_path, "w", encoding="utf-8").write(t)
print("java patched")
PY
echo "apply.sh: done"
