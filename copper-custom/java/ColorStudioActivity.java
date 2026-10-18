package git.artdeell.mojo;

import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Bundle;
import android.text.Editable;
import android.text.InputFilter;
import android.text.InputType;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.SwitchCompat;
import androidx.preference.PreferenceManager;

import com.google.android.material.color.MaterialColors;
import com.google.android.material.dialog.MaterialAlertDialogBuilder;

/**
 * BlockComet Color Studio. Every colour of the launcher is entered as an exact hex / RGB value. The screen itself is
 * re-created after each change, so it doubles as a live preview of the whole launcher.
 */
public class ColorStudioActivity extends AppCompatActivity {
    private SharedPreferences mPrefs;
    private int mOnSurface;
    private int mOnSurfaceVariant;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        mPrefs = PreferenceManager.getDefaultSharedPreferences(this);
        int surface = MaterialColors.getColor(this, com.google.android.material.R.attr.colorSurface, Color.WHITE);
        mOnSurface = MaterialColors.getColor(this, com.google.android.material.R.attr.colorOnSurface, Color.BLACK);
        mOnSurfaceVariant = MaterialColors.getColor(this, com.google.android.material.R.attr.colorOnSurfaceVariant, Color.GRAY);

        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(surface);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        int pad = dp(16);
        root.setPadding(pad, dp(28), pad, pad);
        scroll.addView(root, new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView title = text(getString(R.string.studio_title), 22, mOnSurface);
        title.setTypeface(title.getTypeface(), Typeface.BOLD);
        root.addView(title);

        SwitchCompat enable = new SwitchCompat(this);
        enable.setText(R.string.studio_enable);
        enable.setTextColor(mOnSurface);
        enable.setChecked(mPrefs.getBoolean(BlockCometStudio.PREF_ENABLED, false));
        enable.setPadding(0, dp(12), 0, dp(12));
        enable.setOnCheckedChangeListener((button, checked) -> {
            if (checked == mPrefs.getBoolean(BlockCometStudio.PREF_ENABLED, false)) return;
            mPrefs.edit().putBoolean(BlockCometStudio.PREF_ENABLED, checked).apply();
            recreate();
        });
        root.addView(enable);

        if (Build.VERSION.SDK_INT < 30) {
            TextView note = text(getString(R.string.studio_note_old), 13, mOnSurfaceVariant);
            note.setPadding(0, 0, 0, dp(8));
            root.addView(note);
        }

        String[] names = getResources().getStringArray(R.array.studio_role_names);
        for (int role = 0; role < BlockCometStudio.ROLE_COUNT; role++) {
            root.addView(buildRow(role, names[role]));
        }

        LinearLayout buttons = new LinearLayout(this);
        buttons.setOrientation(LinearLayout.HORIZONTAL);
        buttons.setPadding(0, dp(16), 0, 0);
        buttons.addView(button(R.string.studio_presets, v -> showPresets()), weight());
        buttons.addView(button(R.string.studio_reset, v -> {
            BlockCometStudio.reset(mPrefs);
            recreate();
        }), weight());
        buttons.addView(button(R.string.studio_done, v -> finish()), weight());
        root.addView(buttons);

        setContentView(scroll);
    }

    private View buildRow(int role, String name) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setPadding(0, dp(8), 0, dp(8));
        int color = BlockCometStudio.get(mPrefs, role);

        View swatch = new View(this);
        GradientDrawable shape = new GradientDrawable();
        shape.setColor(color);
        shape.setCornerRadius(dp(10));
        shape.setStroke(dp(1), mOnSurfaceVariant);
        swatch.setBackground(shape);
        row.addView(swatch, new LinearLayout.LayoutParams(dp(44), dp(44)));

        TextView label = text(name, 16, mOnSurface);
        LinearLayout.LayoutParams labelParams = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        labelParams.setMarginStart(dp(14));
        row.addView(label, labelParams);

        TextView hex = text(hexOf(color), 14, mOnSurfaceVariant);
        hex.setTypeface(Typeface.MONOSPACE);
        row.addView(hex);

        row.setOnClickListener(v -> showPicker(role, name));
        return row;
    }

    private void showPicker(int role, String roleName) {
        int current = BlockCometStudio.get(mPrefs, role);
        final int[] rgb = {Color.red(current), Color.green(current), Color.blue(current)};
        final boolean[] updating = {false};

        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        int pad = dp(20);
        box.setPadding(pad, dp(12), pad, 0);

        final View preview = new View(this);
        box.addView(preview, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)));

        final EditText hex = new EditText(this);
        hex.setSingleLine(true);
        hex.setTypeface(Typeface.MONOSPACE);
        hex.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS);
        hex.setFilters(new InputFilter[]{new InputFilter.LengthFilter(7)});
        hex.setHint(R.string.studio_hex_hint);
        box.addView(hex);

        final SeekBar[] bars = new SeekBar[3];
        String[] letters = {"R", "G", "B"};
        for (int i = 0; i < 3; i++) {
            LinearLayout line = new LinearLayout(this);
            line.setOrientation(LinearLayout.HORIZONTAL);
            line.setGravity(Gravity.CENTER_VERTICAL);
            line.addView(text(letters[i], 14, mOnSurface), new LinearLayout.LayoutParams(dp(20), ViewGroup.LayoutParams.WRAP_CONTENT));
            SeekBar bar = new SeekBar(this);
            bar.setMax(255);
            bar.setProgress(rgb[i]);
            bars[i] = bar;
            line.addView(bar, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
            box.addView(line);
            final int channel = i;
            bar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                    if (!fromUser) return;
                    rgb[channel] = progress;
                    updating[0] = true;
                    hex.setText(hexOf(Color.rgb(rgb[0], rgb[1], rgb[2])));
                    updating[0] = false;
                    preview.setBackgroundColor(Color.rgb(rgb[0], rgb[1], rgb[2]));
                }
                @Override public void onStartTrackingTouch(SeekBar seekBar) {}
                @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            });
        }

        hex.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {}
            @Override public void afterTextChanged(Editable s) {
                if (updating[0]) return;
                String value = s.toString().trim();
                if (!value.startsWith("#")) value = "#" + value;
                if (value.length() != 7) return;
                try {
                    int parsed = Color.parseColor(value);
                    rgb[0] = Color.red(parsed);
                    rgb[1] = Color.green(parsed);
                    rgb[2] = Color.blue(parsed);
                    updating[0] = true;
                    for (int i = 0; i < 3; i++) bars[i].setProgress(rgb[i]);
                    updating[0] = false;
                    preview.setBackgroundColor(parsed);
                } catch (IllegalArgumentException ignored) {
                    // not a colour (yet)
                }
            }
        });
        updating[0] = true;
        hex.setText(hexOf(current));
        updating[0] = false;
        preview.setBackgroundColor(current);

        new MaterialAlertDialogBuilder(this)
                .setTitle(roleName)
                .setView(box)
                .setPositiveButton(R.string.studio_apply, (dialog, which) -> {
                    BlockCometStudio.set(mPrefs, role, Color.rgb(rgb[0], rgb[1], rgb[2]));
                    recreate();
                })
                .setNegativeButton(android.R.string.cancel, null)
                .show();
    }

    private void showPresets() {
        int[] ids = BlockCometStudio.PRESET_NAMES;
        String[] items = new String[ids.length];
        for (int i = 0; i < ids.length; i++) items[i] = getString(ids[i]);
        new MaterialAlertDialogBuilder(this)
                .setTitle(R.string.studio_presets)
                .setItems(items, (dialog, which) -> {
                    BlockCometStudio.applyPreset(mPrefs, which);
                    recreate();
                })
                .show();
    }

    private TextView text(String value, int sp, int color) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(sp);
        view.setTextColor(color);
        return view;
    }

    private Button button(int label, View.OnClickListener listener) {
        Button button = new Button(this);
        button.setText(label);
        button.setOnClickListener(listener);
        return button;
    }

    private LinearLayout.LayoutParams weight() {
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        params.setMarginEnd(dp(6));
        return params;
    }

    private static String hexOf(int color) {
        return String.format("#%06X", color & 0xFFFFFF);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
