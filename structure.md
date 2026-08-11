.
├── .gitignore
├── CODE_OF_CONDUCT.md
├── LICENSE
├── config.json
├── main.py
├── requirements.txt
├── rules.md
├── app/
│   ├── presentation/
│   │   └── gui.py
│   └── services/
│       ├── agent.py
│       ├── apps.py
│       ├── config.py
│       ├── device.py
│       ├── executors.py
│       ├── llm.py
│       ├── parser.py
│       ├── prompt.py
│       ├── sessions.py
│       ├── tools.py
│       └── window_manager.py
├── components/
│   ├── confirm.py
│   ├── sidebar.py
│   └── icons/
│       ├── chat.svg
│       ├── eye.svg
│       ├── eye_off.svg
│       ├── image.svg
│       ├── info.svg
│       ├── send.svg
│       ├── session.svg
│       ├── settings.svg
│       ├── skills.svg
│       ├── stop.svg
│       └── trash.svg
├── lib/
│   └── languages.json
├── pages/
│   ├── chat_page.py
│   ├── gallery_page.py
│   ├── info_page.py
│   ├── session_page.py
│   ├── settings_page.py
│   └── skills_page.py
├── skills/
│   ├── chrome/
│   │   ├── _cdp.py
│   │   ├── chrome_shortcuts.py
│   │   └── chrome_tabs.py
│   └── general/
│       ├── _click_try.py
│       ├── _mouse.py
│       ├── app_launcher.py
│       ├── app_refocus.py
│       ├── back.py
│       ├── close_app.py
│       ├── double_click.py
│       ├── drag.py
│       ├── expand_window.py
│       ├── file_ops.py
│       ├── find_and_click.py
│       ├── forward.py
│       ├── hold_left_click.py
│       ├── keyboard_controls.py
│       ├── left_click.py
│       ├── minimize_window.py
│       ├── ocr.py
│       ├── right_click.py
│       ├── screenshot.py
│       ├── scroll_down.py
│       ├── scroll_up.py
│       ├── switch_app.py
│       ├── switch_desktop.py
│       ├── try_click.py
│       └── window_focus.py
├── tests/
│   ├── test_app_launcher.py
│   ├── test_app_refocus.py
│   ├── test_app_reposition.py
│   ├── test_apps.py
│   ├── test_capture_session.py
│   ├── test_chrome_cdp.py
│   ├── test_chrome_shortcuts.py
│   ├── test_click_try.py
│   ├── test_close_app.py
│   ├── test_device.py
│   ├── test_drag.py
│   ├── test_file_ops.py
│   ├── test_keyboard.py
│   ├── test_ocr.py
│   ├── test_recovery.py
│   ├── test_reposition.py
│   ├── test_sessions.py
│   ├── test_settings.py
│   ├── test_smooth_move.py
│   ├── test_tools.py
│   └── test_window_controls.py
