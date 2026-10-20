#!/usr/bin/env python3
"""look_share.py <res-dir> <java-dir> <custom-dir>

"Share my look": two entries in the appearance settings, one that saves colours / font / language / background in a file
(BlockCometLook.export) and one that applies such a file from a friend (BlockCometLook.importLook).
Runs after fonts.py.
"""
import os
import shutil
import sys

res, java, custom = sys.argv[1:4]
shutil.copy(os.path.join(custom, "java", "BlockCometLook.java"), os.path.join(java, "BlockCometLook.java"))

EN = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="blockcomet_look_export_title">Share my look</string>
    <string name="blockcomet_look_export_summary">Saves your colors, Color Studio, font, language and background in one file that you can send to a friend.</string>
    <string name="blockcomet_look_import_title">Import a look from a file</string>
    <string name="blockcomet_look_import_summary">Applies the colors, font and background from a file a friend sent you. Open only files from people you trust.</string>
    <string name="blockcomet_look_exported">Look saved</string>
    <string name="blockcomet_look_export_failed">Could not save the look</string>
    <string name="blockcomet_look_importing">Importing the look…</string>
    <string name="blockcomet_look_imported">Look applied</string>
    <string name="blockcomet_look_import_failed">That file is not a valid BlockComet look</string>
</resources>
"""
AR = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="blockcomet_look_export_title">مشاركة مظهري</string>
    <string name="blockcomet_look_export_summary">يحفظ ألوانك واستوديو الألوان والخط واللغة والخلفية في ملف واحد ترسله لصديقك.</string>
    <string name="blockcomet_look_import_title">استيراد مظهر من ملف</string>
    <string name="blockcomet_look_import_summary">يطبّق الألوان والخط والخلفية من ملف أرسله لك صديق. افتح ملفات من تثق بهم فقط.</string>
    <string name="blockcomet_look_exported">تم حفظ المظهر</string>
    <string name="blockcomet_look_export_failed">تعذّر حفظ المظهر</string>
    <string name="blockcomet_look_importing">جارٍ استيراد المظهر…</string>
    <string name="blockcomet_look_imported">تم تطبيق المظهر</string>
    <string name="blockcomet_look_import_failed">هذا الملف ليس مظهر BlockComet صالحًا</string>
</resources>
"""
open(os.path.join(res, "values", "blockcomet_look_share.xml"), "w", encoding="utf-8").write(EN)
os.makedirs(os.path.join(res, "values-ar"), exist_ok=True)
open(os.path.join(res, "values-ar", "blockcomet_look_share.xml"), "w", encoding="utf-8").write(AR)

xp = os.path.join(res, "xml", "pref_appearance.xml")
x = open(xp, encoding="utf-8").read()
i = x.index('android:key="blockcomet_remove_font"')
j = x.index("/>", i) + 2
prefs = (
    "\n        <androidx.preference.Preference\n"
    '            android:key="blockcomet_look_export"\n'
    '            android:title="@string/blockcomet_look_export_title"\n'
    '            android:summary="@string/blockcomet_look_export_summary"\n'
    '            app:iconSpaceReserved="false" />'
    "\n        <androidx.preference.Preference\n"
    '            android:key="blockcomet_look_import"\n'
    '            android:title="@string/blockcomet_look_import_title"\n'
    '            android:summary="@string/blockcomet_look_import_summary"\n'
    '            app:iconSpaceReserved="false" />'
)
open(xp, "w", encoding="utf-8").write(x[:j] + prefs + x[j:])

fp = os.path.join(java, "prefs", "screens", "LauncherPreferenceAppearanceFragment.java")
f = open(fp, encoding="utf-8").read()
anchor = 'androidx.preference.Preference blockCometLanguage = findPreference("app_language");'
assert anchor in f, "language hook not found"
hook = """final androidx.activity.result.ActivityResultLauncher<String> blockCometLookExport = registerForActivityResult(
                new androidx.activity.result.contract.ActivityResultContracts.CreateDocument(), uri -> {
                    if (uri == null) return;
                    final android.content.Context appContext = requireContext().getApplicationContext();
                    git.artdeell.mojo.MojoApplication.sExecutorService.execute(() -> {
                        boolean ok = git.artdeell.mojo.BlockCometLook.export(appContext, uri);
                        android.app.Activity activity = getActivity();
                        if (activity == null) return;
                        activity.runOnUiThread(() -> android.widget.Toast.makeText(appContext,
                                ok ? R.string.blockcomet_look_exported : R.string.blockcomet_look_export_failed,
                                android.widget.Toast.LENGTH_LONG).show());
                    });
                });
        final androidx.activity.result.ActivityResultLauncher<String[]> blockCometLookImport = registerForActivityResult(
                new androidx.activity.result.contract.ActivityResultContracts.OpenDocument(), uri -> {
                    if (uri == null) return;
                    final android.content.Context appContext = requireContext().getApplicationContext();
                    android.widget.Toast.makeText(appContext, R.string.blockcomet_look_importing, android.widget.Toast.LENGTH_SHORT).show();
                    git.artdeell.mojo.MojoApplication.sExecutorService.execute(() -> {
                        boolean ok = git.artdeell.mojo.BlockCometLook.importLook(appContext, uri);
                        android.app.Activity activity = getActivity();
                        if (activity == null) return;
                        activity.runOnUiThread(() -> {
                            android.widget.Toast.makeText(appContext,
                                    ok ? R.string.blockcomet_look_imported : R.string.blockcomet_look_import_failed,
                                    android.widget.Toast.LENGTH_LONG).show();
                            if (ok) {
                                git.artdeell.mojo.BlockCometLook.applySideEffects(appContext);
                                activity.recreate();
                            }
                        });
                    });
                });
        androidx.preference.Preference blockCometLookExportPref = findPreference("blockcomet_look_export");
        if (blockCometLookExportPref != null) {
            blockCometLookExportPref.setOnPreferenceClickListener(preference -> {
                blockCometLookExport.launch("BlockComet-look.bclook");
                return true;
            });
        }
        androidx.preference.Preference blockCometLookImportPref = findPreference("blockcomet_look_import");
        if (blockCometLookImportPref != null) {
            blockCometLookImportPref.setOnPreferenceClickListener(preference -> {
                blockCometLookImport.launch(new String[]{"*/*"});
                return true;
            });
        }
        """
open(fp, "w", encoding="utf-8").write(f.replace(anchor, hook + anchor, 1))
print("share-my-look wired")
