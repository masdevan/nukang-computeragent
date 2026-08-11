from skills.chrome import _cdp


def _ready():
    return _cdp.debug_status()


def chrome_list_tabs(args):
    ok, message = _ready()
    if not ok:
        return message
    lines = [message]
    for index, tab in enumerate(_cdp.list_tabs()):
        marker = " (active)" if tab["active"] else ""
        lines.append(f"{index}: {tab['title']} — {tab['url']}{marker}")
    return "\n".join(lines)


def chrome_switch_tab(args):
    ok, message = _ready()
    if not ok:
        return message
    tabs = _cdp.list_tabs()
    if not tabs:
        return "No tabs found."
    if "index" in args:
        try:
            chosen = tabs[int(args["index"])]
        except (ValueError, IndexError):
            return f"Invalid tab index: {args['index']}"
    else:
        wanted = args.get("url") or args.get("title") or ""
        chosen = next(
            (tab for tab in tabs if wanted in tab["url"] or wanted in tab["title"]),
            None,
        )
        if chosen is None:
            return f"No tab matches: {wanted}"
    return _cdp.activate_tab(chosen["id"])


def chrome_page_text(args):
    ok, message = _ready()
    if not ok:
        return message
    return _cdp.evaluate("document.body.innerText")


def chrome_enable_debugging(args):
    ok, message = _cdp.enable_debug_chrome()
    return message


def chrome_evaluate(args):
    ok, message = _ready()
    if not ok:
        return message
    return _cdp.evaluate(args["expression"])
