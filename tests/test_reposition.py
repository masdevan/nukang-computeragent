from app.services.tools import choose_app_position

SCREEN = (1920, 1080)
APP_RECT = (0, 0, 640, 480)


def test_point_top_left_moves_app_bottom_right():
    result = choose_app_position(APP_RECT, (100, 100), SCREEN)
    assert result == (1920 - 640 - 8, 1080 - 480 - 8)


def test_point_bottom_right_moves_app_top_left():
    result = choose_app_position(APP_RECT, (1800, 1000), SCREEN)
    assert result == (8, 8)


def test_point_top_right_moves_app_bottom_left():
    result = choose_app_position(APP_RECT, (1800, 100), SCREEN)
    assert result == (8, 1080 - 480 - 8)


def test_point_bottom_left_moves_app_top_right():
    result = choose_app_position(APP_RECT, (100, 1000), SCREEN)
    assert result == (1920 - 640 - 8, 8)


def test_falls_back_when_all_corners_contain_point():
    tiny_screen = (700, 600)
    result = choose_app_position(APP_RECT, (300, 250), tiny_screen)
    assert result in [
        (8, 8),
        (700 - 640 - 8, 8),
        (8, 600 - 480 - 8),
        (700 - 640 - 8, 600 - 480 - 8),
    ]
