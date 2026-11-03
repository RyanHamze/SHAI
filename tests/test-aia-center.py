#!/usr/bin/env python3
"""Run on the Ubuntu graphical test host; no downloads or device actions."""
import importlib.machinery
import faulthandler
import json
import os
import time
import urllib.request

faulthandler.enable()
aia = importlib.machinery.SourceFileLoader("aia_center", "/usr/bin/shai-aia").load_module()
app = aia.AIAApplication()
app.set_flags(app.get_flags() | aia.Gio.ApplicationFlags.NON_UNIQUE)
assert app.register(None)
assert not app.get_is_remote(), "GUI tests require a local application instance"
window = aia.AIAWindow(app)
for tab in window.TABS:
    window.show_tab(tab)
    assert window.pages[tab].get_first_child() is not None, tab
    print("PASS tab", tab, flush=True)
assert "Control Center" in window.TABS
def descendants(widget):
    yield widget
    child = widget.get_first_child()
    while child:
        yield from descendants(child)
        child = child.get_next_sibling()
window.show_tab("Models")
highlights = [x for x in descendants(window.pages["Models"]) if x.has_css_class("model-card") and x.has_css_class("recommended")]
assert len(highlights) == 1
assert "ACTIVE DEFAULT" in " ".join(x.get_label() for x in descendants(highlights[0]) if isinstance(x, aia.Gtk.Label))
assert not any(isinstance(x, aia.Gtk.Button) and x.get_label() == "Test model" for x in descendants(window.pages["Models"]))
assert "Optional browser interface" in " ".join(x.get_label() for x in descendants(window.pages["Models"].get_last_child()) if isinstance(x, aia.Gtk.Label))
print("PASS active-only highlight, removed test action and browser option at bottom", flush=True)
assert window.active_path().is_file()
assert window.service_status()[0] == "ready", window.service_status()
print("PASS active model", window.config["active_model"], flush=True)
answers = []
for prompt in ("What is 7 plus 5? Reply briefly.", "Name one primary color. Reply with one word."):
    answer = window.request_completion([{"role": "user", "content": prompt}], max_tokens=40)
    assert answer.strip()
    answers.append(answer)
    print("PASS inference", repr(answer), flush=True)
assert answers[0] != answers[1]
with urllib.request.urlopen(aia.BROKER_URL + "/health", timeout=3) as response:
    assert json.load(response)["status"] == "ready"
print("PASS broker connection", flush=True)
# Exercise the actual chat submission callback and its GTK async completion.
window.show_tab("Chat")
window.chat_entry.set_text("Name one primary color. Reply briefly.")
window.send_chat(window.chat_entry)
deadline = time.monotonic() + 60
while window.busy and time.monotonic() < deadline:
    while aia.GLib.MainContext.default().pending():
        aia.GLib.MainContext.default().iteration(False)
    time.sleep(0.05)
assert not window.busy, "Chat submission did not complete"
assert window.chat_messages[-1][0] == "AIA"
assert window.chat_messages[-1][1].strip() and "unavailable" not in window.chat_messages[-1][1].lower(), window.chat_messages
print("PASS actual chat callback", repr(window.chat_messages[-1][1]), flush=True)
original = window.config["active_model"]
try:
    for model in aia.installed_catalog_models():
        window.make_default(model)
        deadline = time.monotonic() + 30
        while not window.server_ready() and time.monotonic() < deadline:
            time.sleep(0.2)
        assert window.service_status()[0] == "ready", (model["id"], window.service_status())
        assert window.active_path() == aia.model_path(model)
        print("PASS default switch and process model path", model["id"], flush=True)
finally:
    window.make_default(next(x for x in aia.MODELS if x["id"] == original))
    deadline = time.monotonic() + 30
    while not window.server_ready() and time.monotonic() < deadline:
        time.sleep(0.2)
    assert window.service_status()[0] == "ready"
window.destroy()
