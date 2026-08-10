from app.services.device import format_device_info


def test_format_device_info_fields():
    info = {
        "os": "Windows 11 Pro",
        "screen": "Screen 1 (primary): 1920x1080 @ 100%",
        "cpu": "Intel Core i5",
        "ram_gb": 8,
    }
    text = format_device_info(info)
    assert "OS: Windows 11 Pro" in text
    assert "Screen: Screen 1 (primary): 1920x1080 @ 100%" in text
    assert "CPU: Intel Core i5" in text
    assert "RAM: 8 GB" in text
