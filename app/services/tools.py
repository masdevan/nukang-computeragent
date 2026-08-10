from app.services.executors import (
    EXECUTORS, app_refocus, back, capture_region, capture_screen, click,
    close_app, double_click, drag, execute_tool, find_and_click,
    focus_window, forward, get_device_info, launch_app, list_desktops,
    list_windows, move_by, move_to, position, press_combo, press_key,
    read_file, run_command, scroll, try_click, type_text,
)
from app.services.parser import (
    extract_json_blocks, format_call, looks_like_tool_attempt, parse_tool_call,
)
from app.services.prompt import MAX_STEPS, SYSTEM_PROMPT, TOOLS, build_system_prompt
from app.services.window_manager import (
    MAIN_WINDOW_HWND, active_screen, choose_app_position, follow_active_desktop,
    main_window_rect, move_window, reposition_app_away, reposition_app_to_corner,
    set_main_window, window_handle_valid,
)
from skills import ocr, screenshot
from skills._mouse import current_position, move_to as mouse_move_to, scroll as mouse_scroll, xbutton
