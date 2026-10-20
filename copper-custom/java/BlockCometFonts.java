package git.artdeell.mojo;

import android.app.Activity;
import android.app.Application;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.Resources;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewTreeObserver;
import android.widget.TextView;

import androidx.preference.PreferenceManager;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * BlockComet fonts.
 *
 * Preset fonts are theme overlays (ThemeOverlay.BlockComet.Font*), applied by ThemeManager. A font file imported by the
 * user (TTF / OTF) cannot be a resource, so after each screen is shown every TextView in it gets that typeface
 * (and new views that appear later, as the layout changes). Texts drawn by dialogs and pop-up windows live in other
 * windows and keep the theme font.
 */
public final class BlockCometFonts implements Application.ActivityLifecycleCallbacks {
    public static final String PREF_FONT = "theme_font";
    public static final String CUSTOM = "custom";
    private static final String CUSTOM_FILE = "custom_font.ttf";
    private static final long MAX_FONT_BYTES = 25L * 1024 * 1024;

    private static Typeface sCustom;
    private static long sCustomStamp = -1;

    /** Call once from Application#onCreate (through ThemeManager.init) */
    public static void install(Application application) {
        application.registerActivityLifecycleCallbacks(new BlockCometFonts());
    }

    /** The preset font chosen in the settings, as a theme overlay. */
    public static void applyTheme(Activity activity, SharedPreferences preferences) {
        Resources.Theme theme = activity.getTheme();
        String choice = preferences.getString(PREF_FONT, "poppins");
        switch (choice) {
            case "system": theme.applyStyle(R.style.ThemeOverlay_BlockComet_SystemFont, true); break;
/*CASES*/
            default: break;
        }
    }

    // ---- the user's own font file ----------------------------------------------------------------------------

    private static File customFile(Context context) {
        return new File(context.getFilesDir(), CUSTOM_FILE);
    }

    public static File getCustomFont(Context context) {
        return customFile(context);
    }

    public static boolean hasCustom(Context context) {
        File file = customFile(context);
        return file.isFile() && file.length() > 0;
    }

    /** Copies the chosen file, checks that it is a font, and makes it the active font. */
    public static boolean importFont(Context context, Uri uri) {
        File target = customFile(context);
        File temp = new File(context.getFilesDir(), CUSTOM_FILE + ".tmp");
        try (InputStream in = context.getContentResolver().openInputStream(uri);
             OutputStream out = new FileOutputStream(temp)) {
            if (in == null) return false;
            byte[] buffer = new byte[64 * 1024];
            long total = 0;
            int read;
            while ((read = in.read(buffer)) > 0) {
                total += read;
                if (total > MAX_FONT_BYTES) {
                    temp.delete();
                    return false;
                }
                out.write(buffer, 0, read);
            }
        } catch (Exception e) {
            temp.delete();
            return false;
        }
        if (!looksLikeFont(temp)) {
            temp.delete();
            return false;
        }
        try {
            Typeface.createFromFile(temp);
        } catch (Exception e) {
            temp.delete();
            return false;
        }
        if (target.exists() && !target.delete()) {
            temp.delete();
            return false;
        }
        if (!temp.renameTo(target)) return false;
        sCustom = null;
        sCustomStamp = -1;
        PreferenceManager.getDefaultSharedPreferences(context).edit().putString(PREF_FONT, CUSTOM).apply();
        return true;
    }

    public static void removeCustom(Context context) {
        customFile(context).delete();
        sCustom = null;
        sCustomStamp = -1;
        SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(context);
        if (CUSTOM.equals(preferences.getString(PREF_FONT, "poppins"))) {
            preferences.edit().putString(PREF_FONT, "poppins").apply();
        }
    }

    private static boolean looksLikeFont(File file) {
        try (InputStream in = new FileInputStream(file)) {
            byte[] magic = new byte[4];
            if (in.read(magic) != 4) return false;
            String text = new String(magic, StandardCharsets.ISO_8859_1);
            return (magic[0] == 0 && magic[1] == 1 && magic[2] == 0 && magic[3] == 0)
                    || text.equals("OTTO") || text.equals("true") || text.equals("ttcf");
        } catch (Exception e) {
            return false;
        }
    }

    private static Typeface loadCustom(Context context) {
        File file = customFile(context);
        if (!file.isFile()) return null;
        if (sCustom != null && sCustomStamp == file.lastModified()) return sCustom;
        try {
            sCustom = Typeface.createFromFile(file);
            sCustomStamp = file.lastModified();
        } catch (Exception e) {
            sCustom = null;
        }
        return sCustom;
    }

    private static void sweep(View view, Typeface typeface) {
        if (view instanceof TextView) {
            TextView text = (TextView) view;
            if (text.getTag(R.id.blockcomet_font_applied) != typeface) {
                Typeface current = text.getTypeface();
                int style = current == null ? Typeface.NORMAL : current.getStyle();
                text.setTypeface(typeface, style);
                text.setTag(R.id.blockcomet_font_applied, typeface);
            }
        }
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) sweep(group.getChildAt(i), typeface);
        }
    }

    private static final class Sweeper implements ViewTreeObserver.OnGlobalLayoutListener {
        private final View mRoot;
        private final Typeface mTypeface;

        Sweeper(View root, Typeface typeface) {
            mRoot = root;
            mTypeface = typeface;
        }

        @Override
        public void onGlobalLayout() {
            sweep(mRoot, mTypeface);
        }
    }

    // ---- lifecycle -------------------------------------------------------------------------------------------

    @Override
    public void onActivityResumed(Activity activity) {
        SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(activity);
        if (!CUSTOM.equals(preferences.getString(PREF_FONT, "poppins"))) return;
        Typeface typeface = loadCustom(activity);
        if (typeface == null) return;
        View decor = activity.getWindow().getDecorView();
        sweep(decor, typeface);
        Sweeper sweeper = new Sweeper(decor, typeface);
        decor.getViewTreeObserver().addOnGlobalLayoutListener(sweeper);
        decor.setTag(R.id.blockcomet_font_sweeper, sweeper);
    }

    @Override
    public void onActivityPaused(Activity activity) {
        View decor = activity.getWindow().getDecorView();
        Object tag = decor.getTag(R.id.blockcomet_font_sweeper);
        if (tag instanceof Sweeper) {
            ViewTreeObserver observer = decor.getViewTreeObserver();
            if (observer.isAlive()) observer.removeOnGlobalLayoutListener((Sweeper) tag);
            decor.setTag(R.id.blockcomet_font_sweeper, null);
        }
    }

    @Override public void onActivityCreated(Activity activity, Bundle savedInstanceState) {}
    @Override public void onActivityStarted(Activity activity) {}
    @Override public void onActivityStopped(Activity activity) {}
    @Override public void onActivitySaveInstanceState(Activity activity, Bundle outState) {}
    @Override public void onActivityDestroyed(Activity activity) {}
}
