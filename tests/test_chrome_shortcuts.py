from skills.chrome import chrome_shortcuts


class FakeKeyboard:
    def __init__(self):
        self.combos = []
        self.typed = []
        self.keys = []

    def press_combo(self, combo):
        self.combos.append(combo)

    def type_text(self, text):
        self.typed.append(text)

    def press_key(self, key):
        self.keys.append(key)


def test_shortcut_combos(monkeypatch):
    fake = FakeKeyboard()
    monkeypatch.setattr(chrome_shortcuts, "KeyboardController", lambda: fake)
    assert chrome_shortcuts.chrome_new_tab({}) == "Pressed ctrl+t"
    assert chrome_shortcuts.chrome_close_tab({}) == "Pressed ctrl+w"
    assert chrome_shortcuts.chrome_reopen_tab({}) == "Pressed ctrl+shift+t"
    assert chrome_shortcuts.chrome_next_tab({}) == "Pressed ctrl+tab"
    assert chrome_shortcuts.chrome_prev_tab({}) == "Pressed ctrl+shift+tab"
    assert chrome_shortcuts.chrome_new_window({}) == "Pressed ctrl+n"
    assert chrome_shortcuts.chrome_incognito({}) == "Pressed ctrl+shift+n"
    assert chrome_shortcuts.chrome_address({}) == "Pressed ctrl+l"
    assert chrome_shortcuts.chrome_reload({}) == "Pressed ctrl+r"
    assert chrome_shortcuts.chrome_history({}) == "Pressed ctrl+h"
    assert chrome_shortcuts.chrome_downloads({}) == "Pressed ctrl+j"
    assert fake.combos == [
        "ctrl+t", "ctrl+w", "ctrl+shift+t", "ctrl+tab", "ctrl+shift+tab",
        "ctrl+n", "ctrl+shift+n", "ctrl+l", "ctrl+r", "ctrl+h", "ctrl+j",
    ]


def test_search_flow(monkeypatch):
    fake = FakeKeyboard()
    monkeypatch.setattr(chrome_shortcuts, "KeyboardController", lambda: fake)
    result = chrome_shortcuts.chrome_search({"query": "cara buat pancake"})
    assert result == "Searched: cara buat pancake"
    assert fake.combos == ["ctrl+l"]
    assert fake.typed == ["cara buat pancake"]
    assert fake.keys == ["enter"]


def test_find_flow(monkeypatch):
    fake = FakeKeyboard()
    monkeypatch.setattr(chrome_shortcuts, "KeyboardController", lambda: fake)
    assert chrome_shortcuts.chrome_find({"text": "hello"}) == "Find: hello"
    assert fake.combos == ["ctrl+f"]
    assert fake.typed == ["hello"]
