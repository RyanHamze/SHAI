# SHAI desktop theme source

This directory contains the reviewed visual assets imported from
`branding/shai-theme.zip` on 2026-10-31. The archive checksum was:

`596a7dcfd7f6e402dcfe487ea8ea0be94596568f38d5cf325b85f990f06d3d4d`

Only the wallpapers, icon theme, GTK color stylesheet, and GNOME Shell
stylesheet are incorporated into the installer. The archive's activation
scripts are retained only in the original ZIP and are not packaged or run.
SHAI uses `shai-theme-apply` instead so settings are backed up as inert JSON,
activation is reversible, and a missing User Themes extension is reported
without triggering a silent network download.

The GNOME Shell stylesheet is derived from GNOME Shell 50.1 and retains its
upstream LGPL-2.1-or-later notice in the file header. SHAI artwork and icons
remain subject to the project branding provenance records.

## Wallpaper revision

The current wallpaper master is
`source/shai-wallpaper-wordmark-master.png`. It was produced with the built-in
image-generation edit workflow from the previous grid wallpaper and the
project's exact SHAI wordmark reference. Production exports retain the dark
green grid and left-side working space while clearly spelling SHAI on the
right. The master was exported at 1920x1080, 2560x1440, and 3840x2160 using
high-quality bicubic scaling.

Final edit prompt: preserve the existing dark green grid, colors, restrained
glow, and empty left working area; replace only the right-side `Ai` mark with
the complete supplied SHAI wordmark in `#33EE33`; add no tagline, Ubuntu
branding, orange, watermark, or decorative elements.
