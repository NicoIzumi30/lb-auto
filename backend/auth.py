import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .database import connect, row_to_dict

SECRET = os.getenv("LB_AUTO_SECRET", "lb-auto-change-this-secret-in-production")
TOKEN_TTL = 60 * 60 * 12
security = HTTPBearer(auto_error=False)

ROLE_OWNER = "ROLE_OWNER"
ROLE_BUYER = "ROLE_BUYER"
ROLE_INSPECTOR_LEAD = "ROLE_INSPECTOR_LEAD"
ROLE_FIELD_CHECKER = "ROLE_FIELD_CHECKER"
ROLE_REPAIR_PIC = "ROLE_REPAIR_PIC"
ROLE_SALES = "ROLE_SALES"
ROLE_LEGAL = "ROLE_LEGAL"
ROLE_HOD = "ROLE_HOD"

ROLES = [ROLE_OWNER, ROLE_HOD, ROLE_BUYER, ROLE_INSPECTOR_LEAD, ROLE_FIELD_CHECKER, ROLE_LEGAL, ROLE_REPAIR_PIC, ROLE_SALES]


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 210_000)
    return f"pbkdf2_sha256$210000${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        _, iterations, salt, expected = encoded.split("$", 3)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.urlsafe_b64decode(salt), int(iterations))
        return hmac.compare_digest(base64.urlsafe_b64encode(digest).decode(), expected)
    except (ValueError, TypeError):
        return False


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_token(user: dict) -> str:
    payload = _b64(json.dumps({"sub": user["id"], "role": user["role"], "exp": int(time.time()) + TOKEN_TTL}, separators=(",", ":")).encode())
    signature = _b64(hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{signature}"


def decode_token(token: str) -> dict:
    try:
        payload, signature = token.split(".", 1)
        expected = _b64(hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        data = json.loads(_unb64(payload))
        if data["exp"] < time.time():
            raise ValueError
        return data
    except (ValueError, KeyError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Sesi tidak valid atau telah berakhir")


def current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Autentikasi diperlukan")
    payload = decode_token(credentials.credentials)
    connection = connect()
    try:
        user = row_to_dict(connection.execute("SELECT id,name,email,phone,role,active,created_at FROM users WHERE id=?", (payload["sub"],)).fetchone())
    finally:
        connection.close()
    if not user or not user["active"]:
        raise HTTPException(status_code=401, detail="Akun tidak aktif")
    return user


def allow(*roles):
    def permission(user: dict = Depends(current_user)):
        if user["role"] != ROLE_OWNER and user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Anda tidak memiliki akses untuk tindakan ini")
        return user
    return permission
