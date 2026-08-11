from skills.general.app_launcher import launch_app, resolve_command_token


def test_launch_unknown_app_returns_error():
    assert launch_app("nama-palsu-xyz") == "Application not found: nama-palsu-xyz"


def test_resolve_command_token_known(monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda name: f"C:/bin/{name}.exe")
    assert resolve_command_token('chrome --profile-directory="Profile 1"') == "chrome"


def test_resolve_command_token_unknown(monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda name: None)
    assert resolve_command_token("google chrome") is None
    assert resolve_command_token("") is None
