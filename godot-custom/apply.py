#!/usr/bin/env python3
"""apply.py <godot-dir>

BlockComet Engine = Godot (MIT) with a different look and layout:
  * name and branding: window/project-manager title, splash, application icon, logos
  * theme: dark grey panels with a blue selection, thin borders, small corner radius, compact spacing (the defaults of a
    fresh editor; the user can still change everything in Editor Settings)
  * layout: the file system dock moves to the bottom next to Output and the debugger, as the "Project" panel of other
    engines; scene tree on the left, inspector on the right.
Every replacement asserts that the text it changes is really there, so a different Godot version fails loudly.
"""
import os
import re
import shutil
import sys

root = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
assets = os.path.join(here, "assets")


def edit(rel, old, new, count=1):
    path = os.path.join(root, rel)
    text = open(path, encoding="utf-8").read()
    assert old in text, f"{rel}: text not found:\n{old}"
    open(path, "w", encoding="utf-8").write(text.replace(old, new, count))


# ---- name -----------------------------------------------------------------------------------------------------------
edit("version.py", 'name = "Godot Engine"', 'name = "BlockComet Engine"')

# ---- theme defaults (a fresh editor) ---------------------------------------------------------------------------------------
S = "editor/settings/editor_settings.cpp"
edit(S, '"interface/theme/color_preset", "Default",', '"interface/theme/color_preset", "Custom",')
edit(S, '"interface/theme/spacing_preset", "Default", "Compact,Default,Spacious,Custom"',
        '"interface/theme/spacing_preset", "Compact", "Compact,Default,Spacious,Custom"')
edit(S, '"interface/theme/base_color", Color(0.14, 0.14, 0.14)', '"interface/theme/base_color", Color(0.22, 0.22, 0.22)')
edit(S, '"interface/theme/accent_color", Color(0.34, 0.62, 1.0)', '"interface/theme/accent_color", Color(0.24, 0.47, 0.76)')
edit(S, '"interface/theme/contrast", 0.3,', '"interface/theme/contrast", 0.2,')
edit(S, '"interface/theme/draw_extra_borders", false,', '"interface/theme/draw_extra_borders", true,')
edit(S, '"interface/theme/border_size", 0,', '"interface/theme/border_size", 1,')
edit(S, '"interface/theme/corner_radius", 4,', '"interface/theme/corner_radius", 2,')

# ---- layout: "Project" panel at the bottom -----------------------------------------------------------------------------------------
edit("editor/docks/filesystem_dock.cpp", "set_default_slot(EditorDock::DOCK_SLOT_LEFT_BR);",
     "set_default_slot(EditorDock::DOCK_SLOT_BOTTOM);")

# ---- branding images -------------------------------------------------------------------------------------------------------------------
shutil.copy(os.path.join(assets, "splash.png"), os.path.join(root, "main", "splash.png"))
shutil.copy(os.path.join(assets, "app_icon.png"), os.path.join(root, "main", "app_icon.png"))

svg = open(os.path.join(assets, "logo.svg"), encoding="utf-8").read()
for name, size in (("TitleBarLogo.svg", 24), ("Godot.svg", 16), ("Logo.svg", 128)):
    sized = re.sub(r'width="512" height="512"', f'width="{size}" height="{size}"', svg, count=1)
    assert f'width="{size}"' in sized, "logo svg has an unexpected header"
    open(os.path.join(root, "editor", "icons", name), "w", encoding="utf-8").write(sized)

print("BlockComet Engine changes applied")
