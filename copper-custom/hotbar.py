#!/usr/bin/env python3
"""hotbar.py <res-dir> <java-dir>

Hotbar touch fixes (taps on the hotbar not selecting a slot):
  * the touch area now has the size of the real hotbar texture (182 x 22 GUI pixels, plus 2 px of slack above the frame)
    and slots are mapped with the real offsets, instead of an approximate 180 x 20 area;
  * every new touch selects its slot (a tap on the slot touched last time used to be ignored when the game had changed
    the selected slot by itself),
  * the GUI scale is read again every time the area is positioned, so a stale value can no longer shrink it;
  * a diagnostic option draws the touch area (red box with slot lines) over the game, to see where it really is.
"""
import os
import sys

res, java = sys.argv[1:3]

p = os.path.join(java, "input", "mouse", "HotbarView.java")
s = open(p, encoding="utf-8").read()


def swap(old, new):
    global s
    assert old in s, "HotbarView changed upstream, anchor not found:\n" + old
    s = s.replace(old, new, 1)


swap("import android.content.Context;\n",
     "import android.content.Context;\nimport android.graphics.Canvas;\nimport android.graphics.Paint;\n")
swap("import androidx.annotation.Nullable;\n",
     "import androidx.annotation.Nullable;\nimport androidx.preference.PreferenceManager;\n")
swap("    private int mGuiScale;\n",
     "    private int mGuiScale;\n    private final Paint mDebugPaint = new Paint();\n")
swap("    private void initialize() {\n        MCOptionUtils.addMCOptionListener(this);\n",
     "    private void initialize() {\n        setWillNotDraw(false);\n        MCOptionUtils.addMCOptionListener(this);\n")

swap("""        marginLayoutParams.width = mWidth = mcScale(180);
        marginLayoutParams.height = height = mcScale(20);
""", """        mGuiScale = MCOptionUtils.getMcScale(); // never position the area with a stale scale
        marginLayoutParams.width = mWidth = mcScale(182); // the hotbar texture is 182 x 22 GUI pixels
        marginLayoutParams.height = height = mcScale(24); // + 2 px of slack above the frame
""")
swap("""        setLayoutParams(marginLayoutParams);
    }
""", """        setLayoutParams(marginLayoutParams);
        invalidate();
    }
""")
swap("        int hotbarIndex = (int)MathUtils.map(x, 0, mWidth, 0, HOTBAR_KEYS.length);\n",
     """        // slot cells are 20 GUI pixels wide and start 1 pixel inside the texture
        int hotbarIndex = (int) ((x - mcScale(1)) / mcScale(20));
        if (hotbarIndex < 0) hotbarIndex = 0;
        if (hotbarIndex >= HOTBAR_KEYS.length) hotbarIndex = HOTBAR_KEYS.length - 1;
""")
# Every new touch selects its slot. The old code remembered the slot of the previous touch and ignored a tap on that same
# slot, so after the game changed the selected slot by itself (server, key, scroll wheel) tapping it again did nothing.
swap("    private int mLastIndex = -1;\n",
     "    private int mLastIndex = -1;\n    private int mPreviousTouchIndex = -1;\n")
swap("""        // Check if the slot changed and we need to make a key press
        if(hotbarIndex == mLastIndex) {
            // Only check for doubletapping if the slot has not changed
            if(hasDoubleTapped && !LauncherPreferences.PREF_DISABLE_SWAP_HAND) CallbackBridge.sendKeyPress(KeyEvent.KEYCODE_F);
            return true;
        }
        mLastIndex = hotbarIndex;
""", """        // A new touch always selects its slot (the game's selected slot can change without us knowing)
        boolean newTouch = actionMasked == MotionEvent.ACTION_DOWN;
        if(newTouch) mLastIndex = -1;
        // Same slot while the finger moves inside it: nothing to send
        if(hotbarIndex == mLastIndex) return true;
        // Double tap on the same slot swaps the hands
        if(newTouch && hasDoubleTapped && hotbarIndex == mPreviousTouchIndex && !LauncherPreferences.PREF_DISABLE_SWAP_HAND) {
            CallbackBridge.sendKeyPress(KeyEvent.KEYCODE_F);
            mLastIndex = hotbarIndex;
            return true;
        }
        mLastIndex = hotbarIndex;
        mPreviousTouchIndex = hotbarIndex;
""")
swap("""    private boolean isLastEventInGesture(int actionMasked) {""", """    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        if (!PreferenceManager.getDefaultSharedPreferences(getContext()).getBoolean("blockcomet_debug_hotbar", false)) return;
        mDebugPaint.setColor(0x66FF2020);
        canvas.drawRect(0, 0, getWidth(), getHeight(), mDebugPaint);
        mDebugPaint.setColor(0xCCFFFFFF);
        mDebugPaint.setStrokeWidth(2f);
        float step = mcScale(20);
        for (int i = 0; i <= HOTBAR_KEYS.length; i++) {
            float lineX = mcScale(1) + i * step;
            canvas.drawLine(lineX, 0, lineX, getHeight(), mDebugPaint);
        }
    }

    private boolean isLastEventInGesture(int actionMasked) {""")
open(p, "w", encoding="utf-8").write(s)

# ---- the diagnostic switch in the appearance settings -----------------------------------------------------------
xp = os.path.join(res, "xml", "pref_appearance.xml")
x = open(xp, encoding="utf-8").read()
i = x.index('android:key="theme_corners"')
j = x.index("/>", i) + 2
pref = (
    "\n        <androidx.preference.SwitchPreferenceCompat\n"
    '            android:defaultValue="false"\n'
    '            android:key="blockcomet_debug_hotbar"\n'
    '            android:title="@string/blockcomet_debug_hotbar_title"\n'
    '            android:summary="@string/blockcomet_debug_hotbar_summary"\n'
    '            app:iconSpaceReserved="false" />'
)
open(xp, "w", encoding="utf-8").write(x[:j] + pref + x[j:])

EN = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="blockcomet_debug_hotbar_title">Show the hotbar touch area</string>
    <string name="blockcomet_debug_hotbar_summary">Diagnostic: draws a red box where taps select hotbar slots. If it is not on top of the hotbar in the game, send a screenshot.</string>
</resources>
"""
AR = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="blockcomet_debug_hotbar_title">إظهار منطقة لمس شريط العناصر</string>
    <string name="blockcomet_debug_hotbar_summary">تشخيص: يرسم مربعًا أحمر حيث يختار الضغط خانات الشريط. إن لم يكن فوق الشريط داخل اللعبة فأرسل لقطة شاشة.</string>
</resources>
"""
open(os.path.join(res, "values", "blockcomet_hotbar.xml"), "w", encoding="utf-8").write(EN)
os.makedirs(os.path.join(res, "values-ar"), exist_ok=True)
open(os.path.join(res, "values-ar", "blockcomet_hotbar.xml"), "w", encoding="utf-8").write(AR)
print("hotbar fixes applied")
