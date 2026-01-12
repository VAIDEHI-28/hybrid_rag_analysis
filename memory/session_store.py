import json
from pathlib import Path

SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)


class SessionStore:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.path = SESSIONS_DIR / f"{session_id}.json"

        if not self.path.exists():
            self._write({"history": []})

    def _read(self):
        return json.loads(self.path.read_text())

    def _write(self, data):
        self.path.write_text(json.dumps(data, indent=2))

    def append(self, item):
        data = self._read()
        data["history"].append(item)
        self._write(data)

    def load(self):
        return self._read()["history"]
