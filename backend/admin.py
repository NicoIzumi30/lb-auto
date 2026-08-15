import argparse
import getpass
import sys

from .auth import ROLES, ROLE_OWNER, hash_password
from .database import db_cursor, init_db, now_iso


def require_user(connection, email):
    user = connection.execute(
        "SELECT id,name,email,role,active FROM users WHERE lower(email)=lower(?)", (email.strip(),)
    ).fetchone()
    if not user:
        raise SystemExit(f"User {email} tidak ditemukan")
    return user


def read_password():
    password = getpass.getpass("Password baru: ")
    confirmation = getpass.getpass("Ulangi password: ")
    if password != confirmation:
        raise SystemExit("Konfirmasi password tidak sama")
    if len(password) < 12:
        raise SystemExit("Password produksi minimal 12 karakter")
    return password


def list_users():
    with db_cursor() as connection:
        rows = connection.execute("SELECT id,name,email,role,active,phone FROM users ORDER BY id").fetchall()
        for row in rows:
            state = "active" if row["active"] else "disabled"
            phone = row["phone"] or "-"
            print(f"{row['id']:>3}  {state:<8}  {row['role']:<22}  {row['email']:<28}  {phone}")


def set_password(email):
    password = read_password()
    with db_cursor() as connection:
        user = require_user(connection, email)
        connection.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(password), user["id"]))
    print(f"Password {email} berhasil diperbarui")


def create_user(args):
    if args.role not in ROLES:
        raise SystemExit(f"Role tidak valid. Pilihan: {', '.join(ROLES)}")
    password = read_password()
    with db_cursor() as connection:
        try:
            connection.execute(
                "INSERT INTO users(name,email,password_hash,role,phone,active,created_at) VALUES(?,?,?,?,?,1,?)",
                (args.name, args.email.lower().strip(), hash_password(password), args.role, args.phone.strip(), now_iso()),
            )
        except Exception as exc:
            if "UNIQUE" in str(exc):
                raise SystemExit("Email sudah digunakan") from exc
            raise
    print(f"User {args.email} berhasil dibuat")


def set_active(email, active):
    with db_cursor() as connection:
        user = require_user(connection, email)
        if not active and user["role"] == ROLE_OWNER:
            active_owners = connection.execute(
                "SELECT COUNT(*) FROM users WHERE role=? AND active=1", (ROLE_OWNER,)
            ).fetchone()[0]
            if active_owners <= 1:
                raise SystemExit("Owner aktif terakhir tidak dapat dinonaktifkan")
        connection.execute("UPDATE users SET active=? WHERE id=?", (int(active), user["id"]))
    print(f"User {email} {'diaktifkan' if active else 'dinonaktifkan'}")


def main():
    parser = argparse.ArgumentParser(description="Administrasi lokal LB AUTO")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list-users", help="Tampilkan semua user")

    password_parser = commands.add_parser("set-password", help="Ganti password user")
    password_parser.add_argument("email")

    create_parser = commands.add_parser("create-user", help="Buat user baru")
    create_parser.add_argument("--name", required=True)
    create_parser.add_argument("--email", required=True)
    create_parser.add_argument("--role", required=True)
    create_parser.add_argument("--phone", default="")

    disable_parser = commands.add_parser("disable-user", help="Nonaktifkan user")
    disable_parser.add_argument("email")
    enable_parser = commands.add_parser("enable-user", help="Aktifkan user")
    enable_parser.add_argument("email")

    args = parser.parse_args()
    init_db()
    if args.command == "list-users":
        list_users()
    elif args.command == "set-password":
        set_password(args.email)
    elif args.command == "create-user":
        create_user(args)
    elif args.command == "disable-user":
        set_active(args.email, False)
    elif args.command == "enable-user":
        set_active(args.email, True)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
