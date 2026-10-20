# Customizing the launcher

Everything below is in **Settings → Launcher appearance**.

## Colors

| Setting | What it does |
|---|---|
| Theme | light, dark or follow the system |
| Color source | the launcher's own blue and white palette, a custom color (Copper's hue picker) or the wallpaper colors (Android 12+) |
| **Color Studio** | ten colors you type as exact `#RRGGBB` values or set with R/G/B sliders; six presets; reset |
| Background and surfaces | follow the accent, white, soft gray, graphite or pure black |

**Color Studio** roles: accent, text on accent, accent container, text on the container, background, cards and panels, text,
secondary text, outlines, secondary accent. The other Material 3 colors are derived from these. The screen re-creates itself
after each change, so it is its own live preview.

Exact colors need **Android 11 or newer** (they use Android's resource override). On older versions the closest ready palette and
surface style are used, and the screen says so.

## Shape and font

* **Corner roundness**: sharp, soft (default), pill.
* **Font**: BlockComet (Poppins; Tajawal when the interface is Arabic), the system font, an imported font, or one of 20 presets:
  Tajawal, Almarai, IBM Plex Sans Arabic, Cairo, Amiri, Noto Kufi Arabic (Arabic + Latin); Lato, Ubuntu, Montserrat, Nunito,
  Quicksand, Rubik, Oswald, Orbitron, Roboto Mono; Press Start 2P, VT323, Silkscreen (pixel); Pacifico, Bebas Neue.
* **Import a font from a file**: pick any `.ttf` or `.otf` you downloaded (up to 25 MB). It is used for the launcher texts on the
  main screens. Pop-up dialogs live in other windows and keep the theme font. **Remove the imported font** returns to the default.

## Language

**Language** lists the 46 languages the launcher ships; Arabic gets a right-to-left layout.

## Background

**Set a custom background** takes an image, a GIF or a video. **Remove** restores the default.

## Share my look

* **Share my look** writes one file (`BlockComet-look.bclook`, a ZIP) containing your colors, Color Studio values, corner and
  surface choices, font (including an imported font file), language, animations and the background image or video.
* **Import a look from a file** applies such a file. Importing reads only known settings with checked values, ignores any other
  content of the file, and limits sizes (background 120 MB, font 25 MB). Even so, open files only from people you trust.

## Troubleshooting touches

**Show the hotbar touch area** draws a red box with slot lines where taps select hotbar slots. If it does not sit on top of the
hotbar in the game, take a screenshot and open an issue; the hotbar position depends on the GUI scale and the resolution
scale of the game.
