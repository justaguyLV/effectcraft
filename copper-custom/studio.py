#!/usr/bin/env python3
"""studio.py <res-dir> <java-dir> <manifest> <custom-dir>

Wires the Color Studio into the launcher: Java classes, "bc_*" colour resources, the overlay that points the theme at
them, strings (English + Arabic), the activity in the manifest, a settings entry and the ThemeManager hook.
Must run after look.py (the fallback uses its surface overlays).
"""
import os
import shutil
import sys

res, java, manifest, custom = sys.argv[1:5]

# ---- Java ------------------------------------------------------------------------------------------------
for name in ("BlockCometStudio.java", "ColorStudioActivity.java"):
    shutil.copy(os.path.join(custom, "java", name), os.path.join(java, name))

# ---- colour resources (defaults = the launcher's own palette) + overlay -------------------------------------
SLOTS = [
    # (resource suffix, theme attribute, default)
    ("primary", "colorPrimary", "#1E88E5"),
    ("on_primary", "colorOnPrimary", "#FFFFFF"),
    ("primary_container", "colorPrimaryContainer", "#D6E8FF"),
    ("on_primary_container", "colorOnPrimaryContainer", "#001B3D"),
    ("secondary", "colorSecondary", "#5B6B7F"),
    ("on_secondary", "colorOnSecondary", "#FFFFFF"),
    ("secondary_container", "colorSecondaryContainer", "#E1E8F4"),
    ("on_secondary_container", "colorOnSecondaryContainer", "#101828"),
    ("background", "android:colorBackground", "#FFFFFF"),
    ("on_background", "colorOnBackground", "#101828"),
    ("surface", "colorSurface", "#FFFFFF"),
    ("on_surface", "colorOnSurface", "#101828"),
    ("surface_variant", "colorSurfaceVariant", "#E1E8F4"),
    ("on_surface_variant", "colorOnSurfaceVariant", "#44505F"),
    ("outline", "colorOutline", "#74808F"),
    ("outline_variant", "colorOutlineVariant", "#C3CBD6"),
    ("surface_dim", "colorSurfaceDim", "#D9DEE8"),
    ("surface_bright", "colorSurfaceBright", "#FFFFFF"),
    ("surface_container_lowest", "colorSurfaceContainerLowest", "#FFFFFF"),
    ("surface_container_low", "colorSurfaceContainerLow", "#F5F8FF"),
    ("surface_container", "colorSurfaceContainer", "#EEF3FC"),
    ("surface_container_high", "colorSurfaceContainerHigh", "#E8EEF8"),
    ("surface_container_highest", "colorSurfaceContainerHighest", "#E1E8F4"),
    ("inverse_surface", "colorSurfaceInverse", "#101828"),
    ("inverse_on_surface", "colorOnSurfaceInverse", "#FFFFFF"),
    ("inverse_primary", "colorPrimaryInverse", "#9CCAFF"),
]

lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
for suffix, _attr, default in SLOTS:
    lines.append(f'    <color name="bc_{suffix}">{default}</color>')
lines.append('    <style name="ThemeOverlay.BlockComet.Studio" parent="">')
for suffix, attr, _default in SLOTS:
    lines.append(f'        <item name="{attr}">@color/bc_{suffix}</item>')
lines.append("    </style>")
lines.append("</resources>")
open(os.path.join(res, "values", "blockcomet_studio_colors.xml"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

# ---- strings -----------------------------------------------------------------------------------------------
EN = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="studio_title">Color Studio</string>
    <string name="studio_enable">Use my colors</string>
    <string name="studio_note_old">On Android 10 and older exact colors are not possible, so the closest ready palette is used.</string>
    <string name="studio_presets">Presets</string>
    <string name="studio_reset">Reset</string>
    <string name="studio_done">Done</string>
    <string name="studio_apply">Apply</string>
    <string name="studio_hex_hint" translatable="false">#RRGGBB</string>
    <string name="studio_open_title">Color Studio</string>
    <string name="studio_open_summary">Exact colors (hex or RGB) for the accent, background, panels, text and more</string>
    <string name="studio_preset_ocean">Ocean (blue and white)</string>
    <string name="studio_preset_sunset">Sunset (orange, dark)</string>
    <string name="studio_preset_mint">Mint (green and white)</string>
    <string name="studio_preset_violet">Violet night (purple, dark)</string>
    <string name="studio_preset_mono">Black and white</string>
    <string name="studio_preset_gold">Gold and graphite</string>
    <string-array name="studio_role_names">
        <item>Accent</item>
        <item>Text on accent</item>
        <item>Accent container</item>
        <item>Text on accent container</item>
        <item>Background</item>
        <item>Cards and panels</item>
        <item>Text</item>
        <item>Secondary text</item>
        <item>Outlines</item>
        <item>Secondary accent</item>
    </string-array>
</resources>
"""
AR = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="studio_title">استوديو الألوان</string>
    <string name="studio_enable">استخدم ألواني</string>
    <string name="studio_note_old">في أندرويد 10 وما قبله لا يمكن تطبيق ألوان دقيقة، فيُستخدم أقرب نمط جاهز.</string>
    <string name="studio_presets">قوالب جاهزة</string>
    <string name="studio_reset">إعادة ضبط</string>
    <string name="studio_done">تم</string>
    <string name="studio_apply">تطبيق</string>
    <string name="studio_open_title">استوديو الألوان</string>
    <string name="studio_open_summary">ألوان دقيقة (HEX أو RGB) للون الأساسي والخلفية واللوحات والنصوص وغيرها</string>
    <string name="studio_preset_ocean">محيط (أزرق وأبيض)</string>
    <string name="studio_preset_sunset">غروب (برتقالي، داكن)</string>
    <string name="studio_preset_mint">نعناع (أخضر وأبيض)</string>
    <string name="studio_preset_violet">ليل بنفسجي (داكن)</string>
    <string name="studio_preset_mono">أبيض وأسود</string>
    <string name="studio_preset_gold">ذهبي وجرافيت</string>
    <string-array name="studio_role_names">
        <item>اللون الأساسي</item>
        <item>النص فوق اللون الأساسي</item>
        <item>حاوية اللون الأساسي</item>
        <item>النص فوق الحاوية</item>
        <item>الخلفية</item>
        <item>البطاقات واللوحات</item>
        <item>النص</item>
        <item>النص الثانوي</item>
        <item>الحدود</item>
        <item>اللون الثانوي</item>
    </string-array>
</resources>
"""
open(os.path.join(res, "values", "blockcomet_studio.xml"), "w", encoding="utf-8").write(EN)
os.makedirs(os.path.join(res, "values-ar"), exist_ok=True)
open(os.path.join(res, "values-ar", "blockcomet_studio.xml"), "w", encoding="utf-8").write(AR)

# ---- manifest: the activity ------------------------------------------------------------------------------------
m = open(manifest, encoding="utf-8").read()
if "ColorStudioActivity" not in m:
    assert "</application>" in m
    activity = '        <activity\n            android:name="git.artdeell.mojo.ColorStudioActivity"\n            android:exported="false" />\n'
    m = m.replace("</application>", activity + "    </application>", 1)
    open(manifest, "w", encoding="utf-8").write(m)

# ---- settings entry, right after the colour picker ---------------------------------------------------------------
xp = os.path.join(res, "xml", "pref_appearance.xml")
x = open(xp, encoding="utf-8").read()
i = x.index("ThemeColorPreference")
j = x.index("/>", i) + 2
entry = (
    "\n        <androidx.preference.Preference\n"
    '            android:key="blockcomet_color_studio"\n'
    '            android:title="@string/studio_open_title"\n'
    '            android:summary="@string/studio_open_summary"\n'
    '            app:iconSpaceReserved="false" />'
)
open(xp, "w", encoding="utf-8").write(x[:j] + entry + x[j:])

fp = os.path.join(java, "prefs", "screens", "LauncherPreferenceAppearanceFragment.java")
f = open(fp, encoding="utf-8").read()
anchor = 'androidx.preference.Preference blockCometLanguage = findPreference("app_language");'
assert anchor in f, "language hook not found (run look.py / apply.sh section 4 first)"
hook = (
    'androidx.preference.Preference blockCometStudio = findPreference("blockcomet_color_studio");\n'
    "        if (blockCometStudio != null) {\n"
    "            blockCometStudio.setOnPreferenceClickListener(preference -> {\n"
    "                startActivity(new android.content.Intent(requireContext(), git.artdeell.mojo.ColorStudioActivity.class));\n"
    "                return true;\n"
    "            });\n"
    "        }\n        "
)
open(fp, "w", encoding="utf-8").write(f.replace(anchor, hook + anchor, 1))

# ---- ThemeManager: the studio wins over every other colour choice -----------------------------------------------
tp = os.path.join(java, "utils", "ThemeManager.java")
t = open(tp, encoding="utf-8").read()
call = "applyBlockCometLook(activity, preferences);"
assert call in t, "look hook not found (run look.py first)"
t = t.replace(call, call + "\n        git.artdeell.mojo.BlockCometStudio.apply(activity, preferences);", 1)
open(tp, "w", encoding="utf-8").write(t)
print("color studio wired")
