.
├── .gitignore
├── CODE_OF_CONDUCT.md
├── LICENSE
├── main.py
├── requirements.txt
├── rules.md
├── app/
│   ├── presentation/
│   │   └── gui.py
│   └── services/
│       ├── agent.py
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
│   ├── _click_try.py
│   ├── _mouse.py
│   ├── app_launcher.py
│   ├── app_refocus.py
│   ├── back.py
│   ├── close_app.py
│   ├── double_click.py
│   ├── drag.py
│   ├── file_ops.py
│   ├── find_and_click.py
│   ├── forward.py
│   ├── hold_left_click.py
│   ├── keyboard_controls.py
│   ├── left_click.py
│   ├── ocr.py
│   ├── right_click.py
│   ├── screenshot.py
│   ├── scroll_down.py
│   ├── scroll_up.py
│   ├── try_click.py
│   └── window_focus.py
└── tests/
    ├── test_device.py
    ├── test_keyboard.py
    ├── test_ocr.py
    ├── test_sessions.py
    ├── test_settings.py
    └── test_tools.py
