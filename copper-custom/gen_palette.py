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
    False: {  # light: white surfaces, blue accents
        "md_primary": "#1E88E5", "md_on_primary": "#FFFFFF",
        "md_primary_container": "#D6E8FF", "md_on_primary_container": "#001B3D",
        "md_inverse_primary": "#9CCAFF",
        "md_background": "#FFFFFF", "md_on_background": "#101828",
        "md_surface": "#FFFFFF", "md_on_surface": "#101828",
        "md_surface_bright": "#FFFFFF", "md_surface_dim": "#D9DEE8",
        "md_surface_variant": "#E1E8F4", "md_on_surface_variant": "#44505F",
        "md_surface_container_lowest": "#FFFFFF", "md_surface_container_low": "#F5F8FF",
        "md_surface_container": "#EEF3FC", "md_surface_container_high": "#E8EEF8",
        "md_surface_container_highest": "#E1E8F4",
        "md_outline": "#74808F", "md_outline_variant": "#C3CBD6",
    },
    True: {  # dark (only if the user picks it): deep blue-grey with light-blue accents
        "md_primary": "#90CAF9", "md_on_primary": "#003258",
        "md_primary_container": "#00497D", "md_on_primary_container": "#D1E4FF",
        "md_inverse_primary": "#1E88E5",
    },
}

for dark, path in ((False, f"{res}/values/colors.xml"), (True, f"{res}/values-night/colors.xml")):
    scheme = SchemeTonalSpot(Hct.from_int(0xFF1E88E5), dark, 0.0)
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
