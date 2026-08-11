import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "sessions"
_id_counter = 0


def session_ranks(sessions):
    ordered = sorted(sessions, key=lambda data: data["created_at"])
    return {data["id"]: index + 1 for index, data in enumerate(ordered)}


class SessionStore:
    def __init__(self, directory=DATA_DIR):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    def create(self):
        global _id_counter
        _id_counter += 1
        session_id = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}{_id_counter:03d}"
        data = {
            "id": session_id,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "messages": [],
        }
        self.save(data)
        return data

    def save(self, data):
        path = self.directory / f"{data['id']}.json"
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load(self, session_id):
        path = self.directory / f"{session_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def delete(self, session_id):
        path = self.directory / f"{session_id}.json"
        path.unlink(missing_ok=True)

    def list_all(self):
        sessions = []
        for path in sorted(self.directory.glob("*.json")):
            sessions.append(json.loads(path.read_text(encoding="utf-8")))
        return sessions
