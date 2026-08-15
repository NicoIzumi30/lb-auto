import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "lb_auto.db"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def db_cursor():
    connection = connect()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def row_to_dict(row):
    if row is None:
        return None
    result = dict(row)
    for key in ("permissions", "payload", "photos", "source_photos", "channels", "items", "media_items", "categories", "work_items", "before_photos", "after_photos"):
        if key in result and isinstance(result[key], str):
            try:
                result[key] = json.loads(result[key])
            except json.JSONDecodeError:
                pass
    return result


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL,
  phone TEXT NOT NULL DEFAULT '',
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS units (
  id TEXT PRIMARY KEY,
  brand TEXT NOT NULL,
  model TEXT NOT NULL,
  year INTEGER NOT NULL,
  color TEXT NOT NULL,
  plate TEXT NOT NULL UNIQUE,
  transmission TEXT NOT NULL,
  km INTEGER NOT NULL DEFAULT 0,
  vin TEXT,
  engine_number TEXT,
  source TEXT NOT NULL,
  seller TEXT NOT NULL,
  seller_phone TEXT NOT NULL,
  location TEXT NOT NULL,
  offer_price INTEGER NOT NULL DEFAULT 0,
  target_price INTEGER NOT NULL DEFAULT 0,
  buy_price INTEGER NOT NULL DEFAULT 0,
  repair_cost INTEGER NOT NULL DEFAULT 0,
  sell_price INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL,
  assigned_checker_id INTEGER,
  tax_due TEXT,
  progress INTEGER NOT NULL DEFAULT 0,
  rejection_reason TEXT,
  source_photos TEXT NOT NULL DEFAULT '[]',
  created_by INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (assigned_checker_id) REFERENCES users(id),
  FOREIGN KEY (created_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS inspections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unit_id TEXT NOT NULL UNIQUE,
  checker_id INTEGER NOT NULL,
  body_score INTEGER NOT NULL,
  major_accident INTEGER NOT NULL,
  flood INTEGER NOT NULL,
  engine_condition TEXT NOT NULL,
  oil_condition TEXT NOT NULL,
  suspension_condition TEXT NOT NULL,
  tax_status TEXT NOT NULL,
  notes TEXT,
  photos TEXT NOT NULL DEFAULT '[]',
  submitted_at TEXT NOT NULL,
  FOREIGN KEY (unit_id) REFERENCES units(id),
  FOREIGN KEY (checker_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS initial_qc (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unit_id TEXT NOT NULL UNIQUE,
  approved INTEGER NOT NULL,
  notes TEXT,
  reviewed_by INTEGER NOT NULL,
  reviewed_at TEXT NOT NULL,
  FOREIGN KEY (unit_id) REFERENCES units(id),
  FOREIGN KEY (reviewed_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS legal_prechecks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unit_id TEXT NOT NULL UNIQUE,
  stnk_available INTEGER NOT NULL,
  bpkb_available INTEGER NOT NULL,
  vin_match INTEGER NOT NULL,
  engine_match INTEGER NOT NULL,
  tax_checked INTEGER NOT NULL,
  notes TEXT,
  approved_by INTEGER NOT NULL,
  approved_at TEXT NOT NULL,
  FOREIGN KEY (unit_id) REFERENCES units(id),
  FOREIGN KEY (approved_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unit_id TEXT NOT NULL UNIQUE,
  voucher_number TEXT NOT NULL UNIQUE,
  amount INTEGER NOT NULL,
  method TEXT NOT NULL,
  proof_url TEXT,
  requested_by INTEGER NOT NULL,
  requested_at TEXT NOT NULL,
  confirmed_by INTEGER,
  paid_at TEXT,
  FOREIGN KEY (unit_id) REFERENCES units(id),
  FOREIGN KEY (requested_by) REFERENCES users(id),
  FOREIGN KEY (confirmed_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS repairs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unit_id TEXT NOT NULL UNIQUE,
  categories TEXT NOT NULL,
  vendor TEXT NOT NULL,
  stage TEXT NOT NULL,
  estimated_cost INTEGER NOT NULL DEFAULT 0,
  actual_cost INTEGER NOT NULL DEFAULT 0,
  progress INTEGER NOT NULL DEFAULT 0,
  target_date TEXT,
  notes TEXT,
  updated_by INTEGER NOT NULL,
  updated_at TEXT NOT NULL,
  handover_at TEXT,
  handover_odometer INTEGER,
  handover_notes TEXT,
  work_items TEXT NOT NULL DEFAULT '[]',
  before_photos TEXT NOT NULL DEFAULT '[]',
  after_photos TEXT NOT NULL DEFAULT '[]',
  qc_status TEXT NOT NULL DEFAULT 'PENDING',
  qc_notes TEXT,
  qc_by INTEGER,
  qc_at TEXT,
  FOREIGN KEY (unit_id) REFERENCES units(id),
  FOREIGN KEY (updated_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unit_id TEXT NOT NULL UNIQUE,
  stnk_status TEXT NOT NULL DEFAULT 'BELUM_DICEK',
  tax_due TEXT,
  plate_due TEXT,
  bpkb_status TEXT NOT NULL DEFAULT 'BELUM_DICEK',
  bpkb_number TEXT,
  invoice_status TEXT NOT NULL DEFAULT 'BELUM_DICEK',
  receipt_available INTEGER NOT NULL DEFAULT 0,
  owner_id_copy INTEGER NOT NULL DEFAULT 0,
  items TEXT NOT NULL DEFAULT '[]',
  ready_for_sale INTEGER NOT NULL DEFAULT 0,
  updated_by INTEGER,
  updated_at TEXT NOT NULL,
  qc_by INTEGER,
  qc_at TEXT,
  FOREIGN KEY (unit_id) REFERENCES units(id),
  FOREIGN KEY (updated_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS leads (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT NOT NULL,
  unit_id TEXT,
  source TEXT NOT NULL,
  status TEXT NOT NULL,
  notes TEXT,
  assigned_to INTEGER,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (unit_id) REFERENCES units(id),
  FOREIGN KEY (assigned_to) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  event_type TEXT NOT NULL,
  starts_at TEXT NOT NULL,
  unit_id TEXT,
  assigned_to INTEGER,
  notes TEXT,
  created_by INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (unit_id) REFERENCES units(id),
  FOREIGN KEY (assigned_to) REFERENCES users(id),
  FOREIGN KEY (created_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS sales (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unit_id TEXT NOT NULL UNIQUE,
  buyer_name TEXT NOT NULL,
  buyer_phone TEXT NOT NULL,
  buyer_nik TEXT,
  buyer_address TEXT,
  payment_scheme TEXT NOT NULL,
  leasing_vendor TEXT,
  tenor_months INTEGER,
  down_payment INTEGER NOT NULL DEFAULT 0,
  final_price INTEGER NOT NULL,
  delivered_at TEXT,
  created_by INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'BOOKED',
  booked_at TEXT,
  finance_reference TEXT,
  finance_approved_at TEXT,
  deal_at TEXT,
  delivery_scheduled_at TEXT,
  delivery_completed_at TEXT,
  notes TEXT,
  FOREIGN KEY (unit_id) REFERENCES units(id),
  FOREIGN KEY (created_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS listings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unit_id TEXT NOT NULL UNIQUE,
  media_items TEXT NOT NULL DEFAULT '[]',
  video_url TEXT,
  cash_price INTEGER NOT NULL,
  credit_price INTEGER NOT NULL,
  description TEXT NOT NULL,
  channels TEXT NOT NULL DEFAULT '[]',
  published_at TEXT,
  updated_by INTEGER NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (unit_id) REFERENCES units(id),
  FOREIGN KEY (updated_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS greetings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unit_id TEXT NOT NULL UNIQUE,
  media_url TEXT,
  rating INTEGER,
  consent INTEGER NOT NULL DEFAULT 0,
  notes TEXT,
  created_by INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (unit_id) REFERENCES units(id),
  FOREIGN KEY (created_by) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS audit_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  action TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id TEXT,
  payload TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS notifications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  role TEXT NOT NULL,
  target TEXT,
  message TEXT NOT NULL,
  event_type TEXT NOT NULL,
  entity_id TEXT,
  status TEXT NOT NULL,
  response TEXT,
  created_at TEXT NOT NULL,
  sent_at TEXT
);
"""


def init_db():
    with db_cursor() as connection:
        connection.executescript(SCHEMA)
        migrations = {
            "users": {"phone": "TEXT NOT NULL DEFAULT ''"},
            "units": {"source_photos": "TEXT NOT NULL DEFAULT '[]'"},
            "repairs": {
                "handover_at": "TEXT", "handover_odometer": "INTEGER", "handover_notes": "TEXT",
                "work_items": "TEXT NOT NULL DEFAULT '[]'", "before_photos": "TEXT NOT NULL DEFAULT '[]'",
                "after_photos": "TEXT NOT NULL DEFAULT '[]'", "qc_status": "TEXT NOT NULL DEFAULT 'PENDING'",
                "qc_notes": "TEXT", "qc_by": "INTEGER", "qc_at": "TEXT",
            },
            "documents": {"qc_by": "INTEGER", "qc_at": "TEXT"},
            "sales": {
                "status": "TEXT NOT NULL DEFAULT 'BOOKED'", "booked_at": "TEXT", "finance_reference": "TEXT",
                "finance_approved_at": "TEXT", "deal_at": "TEXT", "delivery_scheduled_at": "TEXT",
                "delivery_completed_at": "TEXT", "notes": "TEXT",
            },
        }
        for table, columns in migrations.items():
            existing = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
            for column, definition in columns.items():
                if column not in existing:
                    connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        connection.execute("UPDATE leads SET status='CANCELLED' WHERE status='LOST'")


def audit(connection, user_id, action, entity_type, entity_id=None, payload=None):
    connection.execute(
        "INSERT INTO audit_logs(user_id, action, entity_type, entity_id, payload, created_at) VALUES(?,?,?,?,?,?)",
        (user_id, action, entity_type, str(entity_id) if entity_id is not None else None, json.dumps(payload or {}), now_iso()),
    )
