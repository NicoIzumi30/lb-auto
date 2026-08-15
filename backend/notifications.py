import urllib.error
import urllib.parse
import urllib.request

from .config import FONNTE_ENABLED, FONNTE_TOKEN
from .database import now_iso


def _insert(connection, role, target, message, event_type, entity_id, status, response=""):
    connection.execute(
        """INSERT INTO notifications(role,target,message,event_type,entity_id,status,response,created_at,sent_at)
           VALUES(?,?,?,?,?,?,?,?,?)""",
        (role, target, message, event_type, str(entity_id), status, response[:2000], now_iso(), now_iso() if status == "SENT" else None),
    )


def notify_role(connection, role: str, message: str, event_type: str, entity_id: str) -> None:
    users = connection.execute(
        "SELECT name,phone FROM users WHERE role=? AND active=1 AND TRIM(phone)<>''", (role,)
    ).fetchall()
    if not users:
        _insert(connection, role, None, message, event_type, entity_id, "SKIPPED_NO_TARGET")
        return

    for user in users:
        target = f"{user['phone']}|{user['name']}|{role}"
        if not FONNTE_ENABLED or not FONNTE_TOKEN:
            _insert(connection, role, target, message, event_type, entity_id, "SKIPPED_DISABLED")
            continue
        body = urllib.parse.urlencode({
            "target": target,
            "message": message,
            "countryCode": "62",
            "typing": "false",
            "delay": "2",
        }).encode()
        request = urllib.request.Request(
            "https://api.fonnte.com/send",
            data=body,
            headers={"Authorization": FONNTE_TOKEN, "Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                result = response.read().decode("utf-8", errors="replace")
            _insert(connection, role, target, message, event_type, entity_id, "SENT", result)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            _insert(connection, role, target, message, event_type, entity_id, "FAILED", str(exc))
