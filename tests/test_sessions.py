from app.services.sessions import SessionStore, session_ranks


def test_session_ranks_by_creation_order(tmp_path):
    store = SessionStore(tmp_path)
    first = store.create()
    second = store.create()
    ranks = session_ranks(store.list_all())
    assert ranks[first["id"]] == 1
    assert ranks[second["id"]] == 2


def test_session_ranks_ignores_display_order():
    data = [
        {"id": "a", "created_at": "2026-01-02T10:00:00"},
        {"id": "b", "created_at": "2026-01-01T10:00:00"},
    ]
    assert session_ranks(data) == {"a": 2, "b": 1}


def test_create_and_load(tmp_path):
    store = SessionStore(tmp_path)
    data = store.create()
    assert data["messages"] == []
    loaded = store.load(data["id"])
    assert loaded["id"] == data["id"]


def test_save_appends_message(tmp_path):
    store = SessionStore(tmp_path)
    data = store.create()
    data["messages"].append({"role": "user", "content": "hai"})
    store.save(data)
    loaded = store.load(data["id"])
    assert loaded["messages"] == [{"role": "user", "content": "hai"}]


def test_load_missing_returns_none(tmp_path):
    store = SessionStore(tmp_path)
    assert store.load("tidak-ada") is None


def test_delete(tmp_path):
    store = SessionStore(tmp_path)
    data = store.create()
    store.delete(data["id"])
    assert store.load(data["id"]) is None


def test_list_all_sorted_by_name(tmp_path):
    store = SessionStore(tmp_path)
    first = store.create()
    second = store.create()
    sessions = store.list_all()
    assert [s["id"] for s in sessions] == [first["id"], second["id"]]
