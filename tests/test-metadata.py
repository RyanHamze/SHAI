#!/usr/bin/env python3
"""Live ExifTool tests on temporary copies only; never touches user media."""
import importlib.machinery
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

gui = importlib.machinery.SourceFileLoader("metadata_test", "/usr/bin/shai-metadata").load_module()
from gi.repository import Gio
with tempfile.TemporaryDirectory(prefix="shai-metadata-test-") as directory:
    root = Path(directory)
    source = Path("/usr/share/backgrounds/shai/shai-wallpaper-1920x1080.png")
    targets = [root / "single image.png", root / "nested" / "bulk image.png", root / "nested" / "deep" / "another.png"]
    targets[2].parent.mkdir(parents=True)
    for target in targets:
        shutil.copy2(source, target)
        subprocess.run(["exiftool", "-overwrite_original", "-Comment=SHAI private test", str(target)], check=True, capture_output=True)
    assert "SHAI private test" in subprocess.check_output(gui.command(targets[0]), text=True)
    subprocess.run(gui.command(targets[0], remove=True), check=True, capture_output=True)
    assert "SHAI private test" not in subprocess.check_output(gui.command(targets[0]), text=True)
    assert "SHAI private test" in subprocess.check_output(["exiftool", "-json", str(targets[0]) + "_original"], text=True)
    assert "-r" not in gui.command(root, recursive=False, remove=True)
    assert "-r" in gui.command(root, remove=True)
    subprocess.run(gui.command(root, remove=True), check=True, capture_output=True)
    assert "SHAI private test" not in subprocess.check_output(gui.command(targets[1]), text=True)
    assert Path(str(targets[1]) + "_original").is_file()
    assert "SHAI private test" not in subprocess.check_output(gui.command(targets[2]), text=True)
    assert Path(str(targets[2]) + "_original").is_file()
    try:
        gui.command("/", recursive=True, remove=True)
        raise AssertionError("Whole-filesystem target accepted")
    except ValueError:
        pass
    print("PASS individual and recursive folder metadata removal; backups preserved; shell-free paths with spaces; root target refused")
app = gui.App()
app.set_flags(app.get_flags() | Gio.ApplicationFlags.NON_UNIQUE)
assert app.register(None)
window = gui.Window(app)
assert window.get_titlebar() is not None
assert window.recursive.get_active()
window.destroy()
print("PASS graphical metadata cleaner construction")
