from skills.general.keyboard_controls import KeyboardController


def _combo(combo):
    KeyboardController().press_combo(combo)
    return f"Pressed {combo}"


def chrome_new_tab(args):
    return _combo("ctrl+t")


def chrome_close_tab(args):
    return _combo("ctrl+w")


def chrome_reopen_tab(args):
    return _combo("ctrl+shift+t")


def chrome_next_tab(args):
    return _combo("ctrl+tab")


def chrome_prev_tab(args):
    return _combo("ctrl+shift+tab")


def chrome_new_window(args):
    return _combo("ctrl+n")


def chrome_incognito(args):
    return _combo("ctrl+shift+n")


def chrome_address(args):
    return _combo("ctrl+l")


def chrome_search(args):
    keyboard = KeyboardController()
    keyboard.press_combo("ctrl+l")
    keyboard.type_text(args["query"])
    keyboard.press_key("enter")
    return f"Searched: {args['query']}"


def chrome_reload(args):
    return _combo("ctrl+r")


def chrome_find(args):
    keyboard = KeyboardController()
    keyboard.press_combo("ctrl+f")
    keyboard.type_text(args["text"])
    return f"Find: {args['text']}"


def chrome_history(args):
    return _combo("ctrl+h")


def chrome_downloads(args):
    return _combo("ctrl+j")
