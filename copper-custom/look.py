#!/usr/bin/env python3
"""look.py <res-dir> <java-dir>

More customisation for the launcher, each option independent of the accent colour:
  theme_surface  background and surfaces: follow accent / white / soft gray / graphite / pure black
  theme_corners  corner roundness: sharp / soft (default) / pill
  theme_font     typeface: Poppins (bundled) / system font
They are theme overlays applied by ThemeManager on top of the colour source, and a change re-creates the screen.
"""
import os
import sys

res, java = sys.argv[1], sys.argv[2]

SURFACES = {
    "White": dict(bg="#FFFFFF", on="#101828", var="#E9EDF3", onvar="#475467", out="#7A8594", outv="#CBD2DB",
                  inv="#101828", oninv="#F2F4F7", dim="#DEE2E8", bright="#FFFFFF",
                  c0="#FFFFFF", c1="#F7F9FC", c2="#F0F3F8", c3="#E9EDF3", c4="#E2E7EE"),
    "Gray": dict(bg="#F1F2F4", on="#1B1D21", var="#E1E3E8", onvar="#4A4F58", out="#7B818B", outv="#C5C9D0",
                 inv="#25282D", oninv="#F1F2F4", dim="#D6D9DF", bright="#F7F8FA",
                 c0="#FFFFFF", c1="#F5F6F8", c2="#EBEDF0", c3="#E4E6EA", c4="#DDDFE4"),
    "Graphite": dict(bg="#17191D", on="#E6E8EC", var="#2B2F36", onvar="#B8BDC6", out="#7E858F", outv="#3C414A",
                     inv="#E6E8EC", oninv="#202328", dim="#121417", bright="#2C3037",
                     c0="#121417", c1="#1B1D22", c2="#202328", c3="#262A30", c4="#2C3037"),
    "Black": dict(bg="#000000", on="#F2F2F2", var="#1A1A1A", onvar="#B5B5B5", out="#6A6A6A", outv="#2E2E2E",
                  inv="#F2F2F2", oninv="#121212", dim="#000000", bright="#1C1C1C",
                  c0="#000000", c1="#0A0A0A", c2="#101010", c3="#161616", c4="#1C1C1C"),
}
ATTRS = (
    ("android:colorBackground", "bg"), ("colorOnBackground", "on"), ("colorSurface", "bg"),
    ("colorOnSurface", "on"), ("colorSurfaceVariant", "var"), ("colorOnSurfaceVariant", "onvar"),
    ("colorOutline", "out"), ("colorOutlineVariant", "outv"), ("colorSurfaceInverse", "inv"),
    ("colorOnSurfaceInverse", "oninv"), ("colorSurfaceDim", "dim"), ("colorSurfaceBright", "bright"),
    ("colorSurfaceContainerLowest", "c0"), ("colorSurfaceContainerLow", "c1"),
    ("colorSurfaceContainer", "c2"), ("colorSurfaceContainerHigh", "c3"),
    ("colorSurfaceContainerHighest", "c4"),
)

# ---- overlays --------------------------------------------------------------------------------
out = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
for name, c in SURFACES.items():
    out.append(f'    <style name="ThemeOverlay.BlockComet.Surface{name}" parent="">')
    for attr, key in ATTRS:
        out.append(f'        <item name="{attr}">{c[key]}</item>')
    out.append("    </style>")
for kind, sizes in (("Sharp", (4, 6, 8)), ("Pill", (28, 36, 44))):
    for comp, size in zip(("Small", "Medium", "Large"), sizes):
        out.append(f'    <style name="ShapeAppearance.BlockComet.{kind}{comp}" '
                   f'parent="ShapeAppearance.Material3.{comp}Component">')
        out.append('        <item name="cornerFamily">rounded</item>')
        out.append(f'        <item name="cornerSize">{size}dp</item>')
        out.append("    </style>")
    out.append(f'    <style name="ThemeOverlay.BlockComet.Corners{kind}" parent="">')
    for comp in ("Small", "Medium", "Large"):
        out.append(f'        <item name="shapeAppearance{comp}Component">'
                   f'@style/ShapeAppearance.BlockComet.{kind}{comp}</item>')
    out.append("    </style>")
out += [
    '    <style name="ThemeOverlay.BlockComet.SystemFont" parent="">',
    '        <item name="android:fontFamily">sans-serif</item>',
    '        <item name="fontFamily">sans-serif</item>',
    "    </style>",
    "</resources>",
]
open(res + "/values/blockcomet_overlays.xml", "w", encoding="utf-8").write("\n".join(out) + "\n")

# ---- texts -----------------------------------------------------------------------------------
EN = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="blockcomet_surface_title">Background and surfaces</string>
    <string name="blockcomet_corners_title">Corner roundness</string>
    <string name="blockcomet_font_title">Font</string>
    <string-array name="blockcomet_surface_names">
        <item>Follow the accent colour</item>
        <item>White</item>
        <item>Soft gray</item>
        <item>Graphite (dark)</item>
        <item>Pure black (AMOLED)</item>
    </string-array>
    <string-array name="blockcomet_corners_names">
        <item>Sharp</item>
        <item>Soft (default)</item>
        <item>Pill</item>
    </string-array>
    <string-array name="blockcomet_surface_values" translatable="false">
        <item>tinted</item><item>white</item><item>gray</item><item>graphite</item><item>black</item>
    </string-array>
    <string-array name="blockcomet_corners_values" translatable="false">
        <item>sharp</item><item>soft</item><item>pill</item>
    </string-array>
</resources>
"""
AR = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="blockcomet_surface_title">الخلفية والأسطح</string>
    <string name="blockcomet_corners_title">استدارة الزوايا</string>
    <string name="blockcomet_font_title">الخط</string>
    <string-array name="blockcomet_surface_names">
        <item>حسب لون التطبيق</item>
        <item>أبيض</item>
        <item>رمادي فاتح</item>
        <item>جرافيت (داكن)</item>
        <item>أسود كامل (AMOLED)</item>
    </string-array>
    <string-array name="blockcomet_corners_names">
        <item>حادة</item>
        <item>ناعمة (افتراضي)</item>
        <item>دائرية كاملة</item>
    </string-array>
</resources>
"""
open(res + "/values/blockcomet_look.xml", "w", encoding="utf-8").write(EN)
os.makedirs(res + "/values-ar", exist_ok=True)
open(res + "/values-ar/blockcomet_look.xml", "w", encoding="utf-8").write(AR)

# ---- preferences, after the colour picker, inside the Theme category --------------------------
xp = res + "/xml/pref_appearance.xml"
x = open(xp, encoding="utf-8").read()
i = x.index("ThemeColorPreference")
j = x.index("</PreferenceCategory>", i)


def list_pref(key, default, title, names, values):
    return (
        "\n        <androidx.preference.ListPreference\n"
        f'            android:defaultValue="{default}"\n'
        f'            android:key="{key}"\n'
        f'            android:entries="@array/{names}"\n'
        f'            android:entryValues="@array/{values}"\n'
        f'            android:title="@string/{title}"\n'
        '            app:iconSpaceReserved="false"\n'
        '            app:useSimpleSummaryProvider="true" />'
    )


prefs = (
    list_pref("theme_surface", "tinted", "blockcomet_surface_title", "blockcomet_surface_names", "blockcomet_surface_values")
    + list_pref("theme_corners", "soft", "blockcomet_corners_title", "blockcomet_corners_names", "blockcomet_corners_values")
    + "\n    "
)
open(xp, "w", encoding="utf-8").write(x[:j] + prefs + x[j:])

# ---- ThemeManager: apply the choices to every activity ----------------------------------------
tp = java + "/utils/ThemeManager.java"
t = open(tp, encoding="utf-8").read()
stmt = "if (overlay != 0) activity.getTheme().applyStyle(overlay, true);"
assert stmt in t, "colour source statement not found"
k = t.index(stmt)
end = t.index("\n    }\n", k)
t = t[:end] + "\n        applyBlockCometLook(activity, preferences);" + t[end:]

METHOD = """    /** BlockComet: surface style, corner roundness and font, applied on top of the colour source */
    private static void applyBlockCometLook(@NonNull Activity activity, SharedPreferences preferences) {
        android.content.res.Resources.Theme theme = activity.getTheme();
        switch (preferences.getString("theme_surface", "tinted")) {
            case "white": theme.applyStyle(R.style.ThemeOverlay_BlockComet_SurfaceWhite, true); break;
            case "gray": theme.applyStyle(R.style.ThemeOverlay_BlockComet_SurfaceGray, true); break;
            case "graphite": theme.applyStyle(R.style.ThemeOverlay_BlockComet_SurfaceGraphite, true); break;
            case "black": theme.applyStyle(R.style.ThemeOverlay_BlockComet_SurfaceBlack, true); break;
            default: break;
        }
        switch (preferences.getString("theme_corners", "soft")) {
            case "sharp": theme.applyStyle(R.style.ThemeOverlay_BlockComet_CornersSharp, true); break;
            case "pill": theme.applyStyle(R.style.ThemeOverlay_BlockComet_CornersPill, true); break;
            default: break;
        }
    }

"""
cls = t.index("    private static class ColorCallbacks")
t = t[:cls] + METHOD + t[cls:]
open(tp, "w", encoding="utf-8").write(t)

# ---- appearance screen: re-create the screen when one of them changes ------------------------
fp = java + "/prefs/screens/LauncherPreferenceAppearanceFragment.java"
f = open(fp, encoding="utf-8").read()
anchor = 'androidx.preference.Preference blockCometLanguage = findPreference("app_language");'
assert anchor in f, "language hook not found"
LOOP = """for (String lookKey : new String[]{"theme_surface", "theme_corners", "theme_font"}) {
            androidx.preference.Preference lookPref = findPreference(lookKey);
            if (lookPref != null) {
                lookPref.setOnPreferenceChangeListener((preference, newValue) -> {
                    requireView().post(() -> requireActivity().recreate());
                    return true;
                });
            }
        }
        """
open(fp, "w", encoding="utf-8").write(f.replace(anchor, LOOP + anchor, 1))
print("look options added")
