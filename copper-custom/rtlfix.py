#!/usr/bin/env python3
"""rtlfix.py <res-dir>

Right-to-left fixes found on a device:
  * landscape top bar: the account name and the settings button met in the same corner. The spinner now keeps room for
    the button on its end side (the portrait layout already did this).
  * Latin account names were left-aligned inside an RTL layout (Android aligns by paragraph direction); they now align
    to the start edge of the view like the Arabic ones.
  * the in-game screen is always laid out left-to-right: ControlLayout places the hotbar touch area with a left margin,
    which an RTL layout ignores (it measures from the right edge), so in Arabic the area sat at the right edge of the
    screen and taps on the real hotbar did nothing. The game surface and the control buttons are not text and never
    needed mirroring.
"""
import sys

res = sys.argv[1]

p = res + "/layout-land/activity_mojo_ui.xml"
s = open(p, encoding="utf-8").read()
anchor = '''        android:dropDownVerticalOffset="@dimen/_42sdp"
'''
assert anchor in s, "landscape spinner anchor not found"
s = s.replace(anchor, anchor + '        android:paddingEnd="@dimen/_52sdp"\n        tools:ignore="RtlSymmetry"\n', 1)
open(p, "w", encoding="utf-8").write(s)

p = res + "/layout/item_account.xml"
s = open(p, encoding="utf-8").read()
anchor = '        android:gravity="center_vertical"\n'
assert anchor in s, "account item anchor not found"
s = s.replace(anchor, anchor + '        android:textAlignment="viewStart"\n', 1)
open(p, "w", encoding="utf-8").write(s)

p = res + "/layout/activity_basemain.xml"
s = open(p, encoding="utf-8").read()
anchor = 'android:keepScreenOn="true">'
assert anchor in s, "game screen root not found"
s = s.replace(anchor, 'android:keepScreenOn="true"\n\tandroid:layoutDirection="ltr">', 1)
open(p, "w", encoding="utf-8").write(s)
print("rtl fixes applied")
