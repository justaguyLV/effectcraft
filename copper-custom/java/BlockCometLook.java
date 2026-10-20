package git.artdeell.mojo;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;

import androidx.preference.PreferenceManager;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;

import git.artdeell.mojo.utils.LauncherBackground;

/**
 * "Share my look": every visual setting (colours, Color Studio, corners, font, language, animations, background image
 * or video, and an imported font file) saved in one ZIP file that a friend can import.
 *
 * Importing is strict: only the listed preference keys are read, each value is checked against what the launcher
 * accepts, entries are matched by name (never extracted to a path from the file), and the sizes are limited.
 */
public final class BlockCometLook {
    private static final int FORMAT = 1;
    private static final long MAX_JSON = 256 * 1024;
    private static final long MAX_BACKGROUND = 120L * 1024 * 1024;
    private static final long MAX_FONT = 25L * 1024 * 1024;
    private static final String BG_VIDEO = "background.mp4";
    private static final String BG_IMAGE = "background.img";
    private static final String FONT = "font.ttf";
    private static final Pattern LANGUAGE = Pattern.compile("^([A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})?)?$");
    private static final Pattern WORD = Pattern.compile("^[a-z0-9_]{1,24}$");

    private static final String[] MODES = {"system", "light", "dark"};
    private static final String[] SOURCES = {"dynamic", "default", "custom"};
    private static final String[] SURFACES = {"tinted", "white", "gray", "graphite", "black"};
    private static final String[] CORNERS = {"sharp", "soft", "pill"};

    private BlockCometLook() {}

    // ---- export ---------------------------------------------------------------------------------------------

    /** Blocking. @return whether the file was written */
    public static boolean export(Context context, Uri target) {
        SharedPreferences p = PreferenceManager.getDefaultSharedPreferences(context);
        try (OutputStream raw = context.getContentResolver().openOutputStream(target);
             ZipOutputStream zip = new ZipOutputStream(new BufferedOutputStream(raw))) {
            JSONObject prefs = new JSONObject();
            for (String key : new String[]{"theme_mode", "color_source", "theme_surface", "theme_corners", "theme_font", "app_language"}) {
                if (p.contains(key)) prefs.put(key, p.getString(key, ""));
            }
            if (p.contains("theme_custom_color")) prefs.put("theme_custom_color", p.getInt("theme_custom_color", 0));
            for (String key : new String[]{"force_landscape", BlockCometStudio.PREF_ENABLED}) {
                if (p.contains(key)) prefs.put(key, p.getBoolean(key, false));
            }
            for (int role = 0; role < BlockCometStudio.ROLE_COUNT; role++) {
                String key = "studio_c_" + role;
                if (p.contains(key)) prefs.put(key, p.getInt(key, 0));
            }
            Set<String> animations = p.getStringSet("animation_types", null);
            if (animations != null) prefs.put("animation_types", new JSONArray(animations));

            JSONObject root = new JSONObject();
            root.put("format", FORMAT);
            root.put("app", "BlockComet");
            root.put("prefs", prefs);
            String backgroundKind = LauncherBackground.getKind(context);
            if (backgroundKind != null) root.put("backgroundKind", backgroundKind);

            zip.putNextEntry(new ZipEntry("look.json"));
            zip.write(root.toString(2).getBytes(StandardCharsets.UTF_8));
            zip.closeEntry();

            if (backgroundKind != null) {
                addFile(zip, LauncherBackground.KIND_VIDEO.equals(backgroundKind) ? BG_VIDEO : BG_IMAGE, LauncherBackground.getFile());
            }
            if (BlockCometFonts.CUSTOM.equals(p.getString(BlockCometFonts.PREF_FONT, "")) && BlockCometFonts.hasCustom(context)) {
                addFile(zip, FONT, BlockCometFonts.getCustomFont(context));
            }
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private static void addFile(ZipOutputStream zip, String name, File file) throws Exception {
        zip.putNextEntry(new ZipEntry(name));
        try (InputStream in = new FileInputStream(file)) {
            byte[] buffer = new byte[64 * 1024];
            int read;
            while ((read = in.read(buffer)) > 0) zip.write(buffer, 0, read);
        }
        zip.closeEntry();
    }

    // ---- import ---------------------------------------------------------------------------------------------

    /**
     * Blocking, do not call it on the UI thread. Afterwards the caller applies the theme mode and language
     * (see applySideEffects) and re-creates the screen.
     * @return whether the file was a valid look and it was applied
     */
    public static boolean importLook(Context context, Uri source) {
        File dir = new File(context.getCacheDir(), "look_import");
        deleteRecursively(dir);
        if (!dir.mkdirs()) return false;
        try {
            JSONObject root = null;
            File background = null;
            File font = null;
            try (InputStream raw = context.getContentResolver().openInputStream(source)) {
                if (raw == null) return false;
                try (ZipInputStream zip = new ZipInputStream(new BufferedInputStream(raw))) {
                    ZipEntry entry;
                    int entries = 0;
                    while ((entry = zip.getNextEntry()) != null) {
                        if (++entries > 8) return false;
                        String name = entry.getName();
                        if (name.equals("look.json")) {
                            root = new JSONObject(new String(readLimited(zip, MAX_JSON), StandardCharsets.UTF_8));
                        } else if (name.equals(BG_VIDEO) || name.equals(BG_IMAGE)) {
                            background = copyLimited(zip, new File(dir, name), MAX_BACKGROUND);
                            if (background == null) return false;
                        } else if (name.equals(FONT)) {
                            font = copyLimited(zip, new File(dir, FONT), MAX_FONT);
                            if (font == null) return false;
                        }
                        // any other entry is ignored
                    }
                }
            }
            if (root == null || root.optInt("format", 0) != FORMAT) return false;
            JSONObject prefs = root.optJSONObject("prefs");
            if (prefs == null) return false;

            SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(context);
            SharedPreferences.Editor editor = preferences.edit();
            putChoice(editor, prefs, "theme_mode", MODES);
            putChoice(editor, prefs, "color_source", SOURCES);
            putChoice(editor, prefs, "theme_surface", SURFACES);
            putChoice(editor, prefs, "theme_corners", CORNERS);
            putChoice(editor, prefs, "theme_font", context.getResources().getStringArray(R.array.blockcomet_font_values));
            String language = prefs.optString("app_language", null);
            if (language != null && LANGUAGE.matcher(language).matches()) editor.putString("app_language", language);
            putInt(editor, prefs, "theme_custom_color");
            for (int role = 0; role < BlockCometStudio.ROLE_COUNT; role++) putInt(editor, prefs, "studio_c_" + role);
            putBoolean(editor, prefs, "force_landscape");
            putBoolean(editor, prefs, BlockCometStudio.PREF_ENABLED);
            JSONArray animations = prefs.optJSONArray("animation_types");
            if (animations != null && animations.length() <= 8) {
                Set<String> values = new HashSet<>();
                for (int i = 0; i < animations.length(); i++) {
                    String value = animations.optString(i, "");
                    if (WORD.matcher(value).matches()) values.add(value);
                }
                editor.putStringSet("animation_types", values);
            }
            // an imported font is only valid together with its file
            if (font == null && BlockCometFonts.CUSTOM.equals(prefs.optString("theme_font", ""))) {
                editor.putString("theme_font", "poppins");
            }
            if (!editor.commit()) return false;

            if (background != null) LauncherBackground.setFromUri(context, Uri.fromFile(background));
            else if (root.optString("backgroundKind", "").isEmpty()) LauncherBackground.remove(context);
            if (font != null) BlockCometFonts.importFont(context, Uri.fromFile(font));
            return true;
        } catch (Exception e) {
            return false;
        } finally {
            deleteRecursively(dir);
        }
    }

    /** UI thread: the settings that need an explicit call besides being stored. */
    public static void applySideEffects(Context context) {
        SharedPreferences p = PreferenceManager.getDefaultSharedPreferences(context);
        git.artdeell.mojo.utils.ThemeManager.applyThemeMode(p.getString("theme_mode", "system"));
        String tag = p.getString("app_language", "");
        androidx.appcompat.app.AppCompatDelegate.setApplicationLocales(tag.isEmpty()
                ? androidx.core.os.LocaleListCompat.getEmptyLocaleList()
                : androidx.core.os.LocaleListCompat.forLanguageTags(tag));
    }

    // ---- helpers ----------------------------------------------------------------------------------------------

    private static void putChoice(SharedPreferences.Editor editor, JSONObject prefs, String key, String[] allowed) {
        String value = prefs.optString(key, null);
        if (value == null) return;
        for (String candidate : allowed) {
            if (candidate.equals(value)) {
                editor.putString(key, value);
                return;
            }
        }
    }

    private static void putInt(SharedPreferences.Editor editor, JSONObject prefs, String key) {
        if (prefs.has(key) && prefs.optLong(key, Long.MIN_VALUE) != Long.MIN_VALUE) {
            long value = prefs.optLong(key);
            if (value >= Integer.MIN_VALUE && value <= Integer.MAX_VALUE) editor.putInt(key, (int) value);
        }
    }

    private static void putBoolean(SharedPreferences.Editor editor, JSONObject prefs, String key) {
        if (prefs.has(key)) editor.putBoolean(key, prefs.optBoolean(key, false));
    }

    private static byte[] readLimited(InputStream in, long limit) throws Exception {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buffer = new byte[8 * 1024];
        long total = 0;
        int read;
        while ((read = in.read(buffer)) > 0) {
            total += read;
            if (total > limit) throw new IllegalStateException("too large");
            out.write(buffer, 0, read);
        }
        return out.toByteArray();
    }

    private static File copyLimited(InputStream in, File target, long limit) throws Exception {
        try (OutputStream out = new FileOutputStream(target)) {
            byte[] buffer = new byte[64 * 1024];
            long total = 0;
            int read;
            while ((read = in.read(buffer)) > 0) {
                total += read;
                if (total > limit) return null;
                out.write(buffer, 0, read);
            }
        }
        return target;
    }

    private static void deleteRecursively(File file) {
        File[] children = file.listFiles();
        if (children != null) for (File child : children) deleteRecursively(child);
        //noinspection ResultOfMethodCallIgnored
        file.delete();
    }
}
