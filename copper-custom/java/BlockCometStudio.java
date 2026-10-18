package git.artdeell.mojo;

import android.app.Activity;
import android.content.SharedPreferences;
import android.content.res.TypedArray;
import android.os.Build;
import android.util.Log;

import androidx.core.graphics.ColorUtils;

import com.google.android.material.color.ColorResourcesOverride;

import java.util.HashMap;
import java.util.Map;

import git.artdeell.mojo.utils.ThemeManager;

/**
 * BlockComet Color Studio: exact colours chosen by the user (hex / RGB), instead of the nearest of the
 * pre-generated hue palettes.
 *
 * The user edits ten colours. The rest of the Material 3 colour roles are derived from them, then every
 * "bc_*" colour resource is replaced at run time (Android 11+, Material's ColorResourcesOverride) and the
 * ThemeOverlay.BlockComet.Studio overlay, which points the theme attributes at those resources, is applied.
 * Before Android 11 a resource override is not possible, so the closest hue palette and surface style are used.
 */
public final class BlockCometStudio {
    private static final String TAG = "BlockCometStudio";
    public static final String PREF_ENABLED = "studio_enabled";
    private static final String PREF_PREFIX = "studio_c_";

    public static final int ACCENT = 0, ON_ACCENT = 1, ACCENT_CONTAINER = 2, ON_ACCENT_CONTAINER = 3, BACKGROUND = 4,
            CARDS = 5, TEXT = 6, TEXT_SECONDARY = 7, OUTLINE = 8, SECONDARY = 9;
    public static final int ROLE_COUNT = 10;

    /** Preset colours, in the order of the roles above. Preset 0 is the default look of the launcher. */
    public static final int[][] PRESETS = {
            {0xFF1E88E5, 0xFFFFFFFF, 0xFFD6E8FF, 0xFF001B3D, 0xFFFFFFFF, 0xFFEEF3FC, 0xFF101828, 0xFF44505F, 0xFF74808F, 0xFF5B6B7F},
            {0xFFFF6D00, 0xFFFFFFFF, 0xFF3A2111, 0xFFFFD9B8, 0xFF14100D, 0xFF221A14, 0xFFF5EDE6, 0xFFBFAFA2, 0xFF7A6A5C, 0xFFFFB74D},
            {0xFF00A86B, 0xFFFFFFFF, 0xFFCFF5E3, 0xFF00391F, 0xFFFFFFFF, 0xFFEAF7F1, 0xFF0F2A20, 0xFF44594F, 0xFF7C9488, 0xFF4DB6AC},
            {0xFFB388FF, 0xFF1B0A3A, 0xFF3B2A66, 0xFFE6D9FF, 0xFF0F0B1A, 0xFF1A1530, 0xFFEDE7FF, 0xFFB5A9D6, 0xFF6F6694, 0xFF7C4DFF},
            {0xFF000000, 0xFFFFFFFF, 0xFFE6E6E6, 0xFF000000, 0xFFFFFFFF, 0xFFF2F2F2, 0xFF000000, 0xFF4D4D4D, 0xFF8A8A8A, 0xFF333333},
            {0xFFFFC107, 0xFF261A00, 0xFF4D3B00, 0xFFFFE08A, 0xFF17191D, 0xFF22252B, 0xFFECEEF2, 0xFFB8BDC6, 0xFF7E858F, 0xFFFFD54F},
    };
    public static final int[] PRESET_NAMES = {
            R.string.studio_preset_ocean, R.string.studio_preset_sunset, R.string.studio_preset_mint,
            R.string.studio_preset_violet, R.string.studio_preset_mono, R.string.studio_preset_gold,
    };

    private BlockCometStudio() {}

    public static int getDefault(int role) {
        return PRESETS[0][role];
    }

    public static int get(SharedPreferences preferences, int role) {
        return preferences.getInt(PREF_PREFIX + role, getDefault(role)) | 0xFF000000;
    }

    public static void set(SharedPreferences preferences, int role, int color) {
        preferences.edit().putInt(PREF_PREFIX + role, color | 0xFF000000).putBoolean(PREF_ENABLED, true).apply();
    }

    public static void applyPreset(SharedPreferences preferences, int preset) {
        SharedPreferences.Editor editor = preferences.edit();
        for (int role = 0; role < ROLE_COUNT; role++) editor.putInt(PREF_PREFIX + role, PRESETS[preset][role]);
        editor.putBoolean(PREF_ENABLED, true).apply();
    }

    public static void reset(SharedPreferences preferences) {
        SharedPreferences.Editor editor = preferences.edit();
        for (int role = 0; role < ROLE_COUNT; role++) editor.remove(PREF_PREFIX + role);
        editor.putBoolean(PREF_ENABLED, false).apply();
    }

    /** Called by ThemeManager for every activity, after the normal colour source. */
    public static void apply(Activity activity, SharedPreferences preferences) {
        if (!preferences.getBoolean(PREF_ENABLED, false)) return;
        boolean exact = false;
        if (Build.VERSION.SDK_INT >= 30) {
            try {
                ColorResourcesOverride override = ColorResourcesOverride.getInstance();
                exact = override != null && override.applyIfPossible(activity, buildColorMap(preferences));
            } catch (Throwable t) {
                Log.w(TAG, "Exact colours are not available, using the closest palette", t);
            }
        }
        if (exact) {
            activity.getTheme().applyStyle(R.style.ThemeOverlay_BlockComet_Studio, true);
        } else {
            applyClosest(activity, preferences);
        }
    }

    /** Before Android 11: nearest hue palette for the accent, nearest surface style for the background. */
    private static void applyClosest(Activity activity, SharedPreferences preferences) {
        int accent = get(preferences, ACCENT);
        int index = (int) Math.round(ThemeManager.getHue(accent) / 10.0) % 36;
        TypedArray overlays = activity.getResources().obtainTypedArray(R.array.theme_hue_overlays);
        try {
            int overlay = overlays.getResourceId(index, 0);
            if (overlay != 0) activity.getTheme().applyStyle(overlay, true);
        } finally {
            overlays.recycle();
        }
        double luminance = ColorUtils.calculateLuminance(get(preferences, BACKGROUND));
        int surface;
        if (luminance > 0.85) surface = R.style.ThemeOverlay_BlockComet_SurfaceWhite;
        else if (luminance > 0.45) surface = R.style.ThemeOverlay_BlockComet_SurfaceGray;
        else if (luminance > 0.03) surface = R.style.ThemeOverlay_BlockComet_SurfaceGraphite;
        else surface = R.style.ThemeOverlay_BlockComet_SurfaceBlack;
        activity.getTheme().applyStyle(surface, true);
    }

    private static int onColor(int background) {
        return ColorUtils.calculateLuminance(background) > 0.4 ? 0xFF000000 : 0xFFFFFFFF;
    }

    private static int mix(int a, int b, float ratio) {
        return ColorUtils.blendARGB(a, b, ratio) | 0xFF000000;
    }

    /** Fills every "bc_*" colour: the ten chosen ones directly, the others derived from them. */
    private static Map<Integer, Integer> buildColorMap(SharedPreferences p) {
        int accent = get(p, ACCENT), onAccent = get(p, ON_ACCENT);
        int accentContainer = get(p, ACCENT_CONTAINER), onAccentContainer = get(p, ON_ACCENT_CONTAINER);
        int background = get(p, BACKGROUND), cards = get(p, CARDS);
        int text = get(p, TEXT), textSecondary = get(p, TEXT_SECONDARY), outline = get(p, OUTLINE);
        int secondary = get(p, SECONDARY);

        Map<Integer, Integer> m = new HashMap<>();
        m.put(R.color.bc_primary, accent);
        m.put(R.color.bc_on_primary, onAccent);
        m.put(R.color.bc_primary_container, accentContainer);
        m.put(R.color.bc_on_primary_container, onAccentContainer);
        m.put(R.color.bc_secondary, secondary);
        m.put(R.color.bc_on_secondary, onColor(secondary));
        m.put(R.color.bc_secondary_container, mix(background, secondary, 0.22f));
        m.put(R.color.bc_on_secondary_container, text);
        m.put(R.color.bc_background, background);
        m.put(R.color.bc_on_background, text);
        m.put(R.color.bc_surface, background);
        m.put(R.color.bc_on_surface, text);
        m.put(R.color.bc_surface_variant, mix(cards, text, 0.12f));
        m.put(R.color.bc_on_surface_variant, textSecondary);
        m.put(R.color.bc_outline, outline);
        m.put(R.color.bc_outline_variant, mix(background, outline, 0.45f));
        m.put(R.color.bc_surface_dim, mix(background, text, 0.12f));
        m.put(R.color.bc_surface_bright, background);
        m.put(R.color.bc_surface_container_lowest, background);
        m.put(R.color.bc_surface_container_low, mix(background, cards, 0.5f));
        m.put(R.color.bc_surface_container, cards);
        m.put(R.color.bc_surface_container_high, mix(cards, text, 0.06f));
        m.put(R.color.bc_surface_container_highest, mix(cards, text, 0.12f));
        m.put(R.color.bc_inverse_surface, text);
        m.put(R.color.bc_inverse_on_surface, background);
        m.put(R.color.bc_inverse_primary, mix(accent, background, 0.4f));
        return m;
    }
}
