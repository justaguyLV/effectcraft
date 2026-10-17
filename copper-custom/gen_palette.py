#!/usr/bin/env python3
"""gen_palette.py <res-dir>: rewrites the md_* colours of values/colors.xml and values-night/colors.xml with a yellow
Material 3 palette (neutrals from the generator, primary family hand-picked so yellow stays bright)."""
import re, sys
from materialyoucolor.hct import Hct
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors

res = sys.argv[1]
md = MaterialDynamicColors()

def camel(token):  # md_on_primary_container -> onPrimaryContainer
    parts = token[3:].split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])

OVERRIDE = {
    False: {  # light
        "md_primary": "#FFC107", "md_on_primary": "#3A2C00",
        "md_primary_container": "#FFE08A", "md_on_primary_container": "#3A2C00",
        "md_inverse_primary": "#FFC107",
    },
    True: {  # dark
        "md_primary": "#FFC107", "md_on_primary": "#3A2C00",
        "md_primary_container": "#5A4400", "md_on_primary_container": "#FFE08A",
        "md_inverse_primary": "#8A6A00",
    },
}

for dark, path in ((False, f"{res}/values/colors.xml"), (True, f"{res}/values-night/colors.xml")):
    scheme = SchemeTonalSpot(Hct.from_int(0xFFFFC107), dark, 0.0)
    text = open(path, encoding="utf-8").read()
    def repl(m):
        token = m.group(1)
        if token in OVERRIDE[dark]:
            return f'<color name="{token}">{OVERRIDE[dark][token]}</color>'
        if token in ("md_scrim", "md_shadow"):
            return m.group(0)
        dc = getattr(md, camel(token), None)
        if dc is None:
            return m.group(0)
        return f'<color name="{token}">#{dc.get_argb(scheme) & 0xFFFFFF:06X}</color>'
    new = re.sub(r'<color name="(md_[a-z_]+)">#[0-9A-Fa-f]+</color>', repl, text)
    open(path, "w", encoding="utf-8").write(new)
    print(("dark" if dark else "light"), "palette written;", len(re.findall("md_", new)), "tokens")
