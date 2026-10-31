# Privacy controls retained with the Ubuntu desktop

- Preserve GDM, GNOME Shell, GNOME Settings and the working Ubuntu desktop.
- Do not reinstall `ubuntu-desktop` metapackages when that would restore removed printer/scanner packages.
- Preserve PackageKit.
- Preserve Firefox and Snap; a later SHAI switch will control their internet access.
- Preserve `whoopsie-preferences` and reinstall the `whoopsie` package only while its service is pre-masked and unable to start.
- Keep `ubuntu-insights` and Apport absent.
- Set GNOME technical-problem reporting to false.
- Set GNOME location services to false and mask GeoClue so D-Bus activation cannot restart it.
