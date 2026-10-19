#!/usr/bin/env python3
"""fonts.py <res-dir> <java-dir> <custom-dir>

Font support for the launcher:
  * preset fonts (the ttf files fetched by fetch-fonts.sh) as font families + theme overlays + a list in the settings,
  * Arabic UI: the default family becomes Tajawal (Arabic and Latin in one design) instead of falling back to a
    different system font for the Arabic letters,
  * "Import a font from a file" (any .ttf / .otf), applied by BlockCometFonts.
Runs after look.py and studio.py.
"""
import os
import sys

res, java, custom = sys.argv[1:4]
font_dir = os.path.join(res, "font")

# id, display name, Arabic-capable
FONTS = [
    ("tajawal", "Tajawal", True), ("almarai", "Almarai", True), ("plexarabic", "IBM Plex Sans Arabic", True),
    ("cairo", "Cairo", True), ("amiri", "Amiri", True), ("notokufi", "Noto Kufi Arabic", True),
    ("lato", "Lato", False), ("ubuntu", "Ubuntu", False), ("montserrat", "Montserrat", False),
    ("nunito", "Nunito", False), ("quicksand", "Quicksand", False), ("rubik", "Rubik", False),
    ("oswald", "Oswald", False), ("orbitron", "Orbitron", False), ("robotomono", "Roboto Mono", False),
    ("pressstart", "Press Start 2P", False), ("vt323", "VT323", False), ("silkscreen", "Silkscreen", False),
    ("pacifico", "Pacifico", False), ("bebas", "Bebas Neue", False),
]


def have(name):
    return os.path.isfile(os.path.join(font_dir, name + ".ttf"))


def family_xml(files):
    """files: {weight: resource name}"""
    rows = []
    for weight, name in sorted(files.items()):
        rows.append(
            f'    <font android:fontStyle="normal" android:fontWeight="{weight}" android:font="@font/{name}"\n'
            f'        app:fontStyle="normal" app:fontWeight="{weight}" app:font="@font/{name}" />'
        )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<font-family xmlns:android="http://schemas.android.com/apk/res/android"\n'
        '    xmlns:app="http://schemas.android.com/apk/res-auto">\n' + "\n".join(rows) + "\n</font-family>\n"
    )


def weights_for(font_id):
    files = {}
    regular = f"{font_id}_regular" if have(f"{font_id}_regular") else (f"{font_id}_var" if have(f"{font_id}_var") else None)
    if regular is None:
        return None
    files[400] = regular
    if have(f"{font_id}_medium"):
        files[500] = f"{font_id}_medium"
    if have(f"{font_id}_bold"):
        files[700] = f"{font_id}_bold"
    return files


# ---- families + overlays ------------------------------------------------------------------------------------------
available = []
overlay = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>",
           '    <item name="blockcomet_font_applied" type="id" />',
           '    <item name="blockcomet_font_sweeper" type="id" />']
cases = []
for font_id, display, arabic in FONTS:
    files = weights_for(font_id)
    if not files:
        print("font not available, skipped:", font_id)
        continue
    open(os.path.join(font_dir, f"bc_{font_id}.xml"), "w", encoding="utf-8").write(family_xml(files))
    style = "Font" + font_id.capitalize()
    overlay += [
        f'    <style name="ThemeOverlay.BlockComet.{style}" parent="">',
        f'        <item name="android:fontFamily">@font/bc_{font_id}</item>',
        f'        <item name="fontFamily">@font/bc_{font_id}</item>',
        "    </style>",
    ]
    cases.append(f'            case "{font_id}": theme.applyStyle(R.style.ThemeOverlay_BlockComet_{style}, true); break;')
    available.append((font_id, display, arabic))
overlay.append("</resources>")
open(os.path.join(res, "values", "blockcomet_fonts_overlays.xml"), "w", encoding="utf-8").write("\n".join(overlay) + "\n")

# Arabic: the default family is Tajawal (the Latin letters of the default font have no Arabic companion)
tajawal = weights_for("tajawal")
if tajawal:
    os.makedirs(os.path.join(res, "font-ar"), exist_ok=True)
    open(os.path.join(res, "font-ar", "blockcomet_sans.xml"), "w", encoding="utf-8").write(family_xml(tajawal))
    print("Arabic default font: Tajawal")

# ---- Java ---------------------------------------------------------------------------------------------------------------
src = open(os.path.join(custom, "java", "BlockCometFonts.java"), encoding="utf-8").read()
assert "/*CASES*/" in src
open(os.path.join(java, "BlockCometFonts.java"), "w", encoding="utf-8").write(src.replace("/*CASES*/", "\n".join(cases)))

# ---- strings and arrays -----------------------------------------------------------------------------------------------
def array(name, items, translatable=True):
    flag = "" if translatable else ' translatable="false"'
    body = "\n".join(f"        <item>{item}</item>" for item in items)
    return f'    <string-array name="{name}"{flag}>\n{body}\n    </string-array>\n'


names_en = ["BlockComet (Poppins; Tajawal in Arabic)", "System font", "Imported font (from a file)"]
names_ar = ["BlockComet (Poppins؛ وTajawal في العربية)", "خط النظام", "الخط المستورد (من ملف)"]
values = ["poppins", "system", "custom"]
for font_id, display, arabic in available:
    names_en.append(display + (" (Arabic + Latin)" if arabic else ""))
    names_ar.append(display + (" (عربي + لاتيني)" if arabic else ""))
    values.append(font_id)

EN = ('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
      '    <string name="blockcomet_font_import_title">Import a font from a file</string>\n'
      '    <string name="blockcomet_font_import_summary">Pick a .ttf or .otf file you downloaded. It is used for the launcher texts.</string>\n'
      '    <string name="blockcomet_font_remove_title">Remove the imported font</string>\n'
      '    <string name="blockcomet_font_imported">Font imported</string>\n'
      '    <string name="blockcomet_font_import_failed">That file is not a usable font (.ttf or .otf, up to 25 MB)</string>\n'
      '    <string name="blockcomet_font_removed">Imported font removed</string>\n'
      + array("blockcomet_font_names", names_en) + array("blockcomet_font_values", values, False) + "</resources>\n")
AR = ('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
      '    <string name="blockcomet_font_import_title">استيراد خط من ملف</string>\n'
      '    <string name="blockcomet_font_import_summary">اختر ملف .ttf أو .otf نزّلته. يُستخدم لنصوص المشغّل.</string>\n'
      '    <string name="blockcomet_font_remove_title">إزالة الخط المستورد</string>\n'
      '    <string name="blockcomet_font_imported">تم استيراد الخط</string>\n'
      '    <string name="blockcomet_font_import_failed">هذا الملف ليس خطًا صالحًا (.ttf أو .otf، حتى 25 ميغابايت)</string>\n'
      '    <string name="blockcomet_font_removed">تمت إزالة الخط المستورد</string>\n'
      + array("blockcomet_font_names", names_ar) + "</resources>\n")
open(os.path.join(res, "values", "blockcomet_fonts.xml"), "w", encoding="utf-8").write(EN)
os.makedirs(os.path.join(res, "values-ar"), exist_ok=True)
open(os.path.join(res, "values-ar", "blockcomet_fonts.xml"), "w", encoding="utf-8").write(AR)

# ---- settings -------------------------------------------------------------------------------------------------------------
xp = os.path.join(res, "xml", "pref_appearance.xml")
x = open(xp, encoding="utf-8").read()
i = x.index('android:key="theme_corners"')
j = x.index("/>", i) + 2
prefs = (
    "\n        <androidx.preference.ListPreference\n"
    '            android:defaultValue="poppins"\n'
    '            android:key="theme_font"\n'
    '            android:entries="@array/blockcomet_font_names"\n'
    '            android:entryValues="@array/blockcomet_font_values"\n'
    '            android:title="@string/blockcomet_font_title"\n'
    '            app:iconSpaceReserved="false"\n'
    '            app:useSimpleSummaryProvider="true" />'
    "\n        <androidx.preference.Preference\n"
    '            android:key="blockcomet_import_font"\n'
    '            android:title="@string/blockcomet_font_import_title"\n'
    '            android:summary="@string/blockcomet_font_import_summary"\n'
    '            app:iconSpaceReserved="false" />'
    "\n        <androidx.preference.Preference\n"
    '            android:key="blockcomet_remove_font"\n'
    '            android:title="@string/blockcomet_font_remove_title"\n'
    '            app:iconSpaceReserved="false" />'
)
open(xp, "w", encoding="utf-8").write(x[:j] + prefs + x[j:])

fp = os.path.join(java, "prefs", "screens", "LauncherPreferenceAppearanceFragment.java")
f = open(fp, encoding="utf-8").read()
anchor = 'androidx.preference.Preference blockCometLanguage = findPreference("app_language");'
assert anchor in f, "language hook not found"
hook = """final androidx.activity.result.ActivityResultLauncher<String[]> blockCometFontPicker = registerForActivityResult(
                new androidx.activity.result.contract.ActivityResultContracts.OpenDocument(), uri -> {
                    if (uri == null) return;
                    boolean imported = git.artdeell.mojo.BlockCometFonts.importFont(requireContext(), uri);
                    android.widget.Toast.makeText(requireContext(),
                            imported ? R.string.blockcomet_font_imported : R.string.blockcomet_font_import_failed,
                            android.widget.Toast.LENGTH_LONG).show();
                    if (imported) requireActivity().recreate();
                });
        androidx.preference.Preference blockCometImportFont = findPreference("blockcomet_import_font");
        if (blockCometImportFont != null) {
            blockCometImportFont.setOnPreferenceClickListener(preference -> {
                blockCometFontPicker.launch(new String[]{"*/*"});
                return true;
            });
        }
        androidx.preference.Preference blockCometRemoveFont = findPreference("blockcomet_remove_font");
        if (blockCometRemoveFont != null) {
            blockCometRemoveFont.setOnPreferenceClickListener(preference -> {
                git.artdeell.mojo.BlockCometFonts.removeCustom(requireContext());
                android.widget.Toast.makeText(requireContext(), R.string.blockcomet_font_removed, android.widget.Toast.LENGTH_SHORT).show();
                requireActivity().recreate();
                return true;
            });
        }
        """
open(fp, "w", encoding="utf-8").write(f.replace(anchor, hook + anchor, 1))

# ---- ThemeManager ----------------------------------------------------------------------------------------------------------
tp = os.path.join(java, "utils", "ThemeManager.java")
t = open(tp, encoding="utf-8").read()
reg = "application.registerActivityLifecycleCallbacks(new ColorCallbacks());"
look = "applyBlockCometLook(activity, preferences);"
assert reg in t and look in t, "ThemeManager anchors not found"
t = t.replace(reg, reg + "\n        git.artdeell.mojo.BlockCometFonts.install(application);", 1)
t = t.replace(look, look + "\n        git.artdeell.mojo.BlockCometFonts.applyTheme(activity, preferences);", 1)
open(tp, "w", encoding="utf-8").write(t)
print(f"fonts wired: {len(available)} preset fonts + system + imported")
