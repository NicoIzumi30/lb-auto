import json
import uuid
from datetime import datetime
from html import escape
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from .auth import (
    ROLES, ROLE_BUYER, ROLE_FIELD_CHECKER, ROLE_HOD, ROLE_INSPECTOR_LEAD, ROLE_LEGAL, ROLE_REPAIR_PIC,
    ROLE_SALES, allow, create_token, current_user, hash_password, verify_password,
)
from .database import audit, db_cursor, now_iso, row_to_dict
from .schemas import (
    ApprovalInput, AssignmentInput, CreditSimulationInput, DeliveryCompleteInput, DeliveryScheduleInput,
    DocumentInput, EventCreate, FinanceApprovalInput, GreetingInput, InitialQCInput, InspectionInput,
    LeadCreate, LegalPrecheckInput, ListingInput, LeadStatusInput, LoginInput, PaymentConfirmInput,
    PaymentRequestInput, PurchaseDecisionInput, RepairHandoverInput, RepairInput, SaleCreate,
    UnitCreate, UserContactInput, UserCreate, UserStatusInput,
)
from .notifications import notify_role
from .report_exports import build_excel, build_pdf, collect_report_data
from .seed import seed_database

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_database()
    yield


app = FastAPI(title="LB AUTO API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:8542", "http://127.0.0.1:8542"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def cache_policy(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/api/") or path.startswith("/uploads/"):
        response.headers["Cache-Control"] = "private, no-store"
    elif path in {"/", "/index.html", "/app.js", "/styles.css", "/sw.js", "/manifest.webmanifest"}:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


def fetch_unit(connection, unit_id):
    unit = row_to_dict(connection.execute("""SELECT u.*, c.name assigned_checker_name FROM units u LEFT JOIN users c ON c.id=u.assigned_checker_id WHERE u.id=?""", (unit_id,)).fetchone())
    if not unit:
        raise HTTPException(404, "Unit tidak ditemukan")
    unit["inspection"] = row_to_dict(connection.execute("SELECT * FROM inspections WHERE unit_id=?", (unit_id,)).fetchone())
    unit["initial_qc"] = row_to_dict(connection.execute("SELECT * FROM initial_qc WHERE unit_id=?", (unit_id,)).fetchone())
    unit["legal_precheck"] = row_to_dict(connection.execute("SELECT * FROM legal_prechecks WHERE unit_id=?", (unit_id,)).fetchone())
    unit["payment"] = row_to_dict(connection.execute("SELECT * FROM payments WHERE unit_id=?", (unit_id,)).fetchone())
    unit["repair"] = row_to_dict(connection.execute("SELECT * FROM repairs WHERE unit_id=?", (unit_id,)).fetchone())
    unit["documents"] = row_to_dict(connection.execute("SELECT * FROM documents WHERE unit_id=?", (unit_id,)).fetchone())
    unit["sale"] = row_to_dict(connection.execute("SELECT * FROM sales WHERE unit_id=?", (unit_id,)).fetchone())
    unit["listing"] = row_to_dict(connection.execute("SELECT * FROM listings WHERE unit_id=?", (unit_id,)).fetchone())
    unit["greeting"] = row_to_dict(connection.execute("SELECT * FROM greetings WHERE unit_id=?", (unit_id,)).fetchone())
    unit["hpp"] = unit["buy_price"] + unit["repair_cost"]
    unit["profit"] = unit["sell_price"] - unit["hpp"] if unit["sell_price"] else 0
    return unit


def require_status(unit, *statuses):
    if not unit:
        raise HTTPException(404, "Unit tidak ditemukan")
    if unit["status"] not in statuses:
        raise HTTPException(409, f"Tahap tidak valid. Status unit saat ini: {unit['status']}")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "LB AUTO API"}


@app.post("/api/uploads", status_code=201)
async def upload_image(request: Request, category: str = Query(...), user=Depends(current_user)):
    allowed_categories = {"sourcing", "inspection", "payment", "repair_before", "repair_after", "greeting", "listing"}
    if category not in allowed_categories:
        raise HTTPException(422, "Kategori upload tidak valid")
    content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
    extensions = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    if content_type not in extensions:
        raise HTTPException(415, "File harus berupa JPG, PNG, atau WebP")
    body = await request.body()
    if not body or len(body) > 8 * 1024 * 1024:
        raise HTTPException(413, "Ukuran file harus antara 1 byte dan 8 MB")
    folder = UPLOAD_DIR / category
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extensions[content_type]}"
    path = folder / filename
    path.write_bytes(body)
    with db_cursor() as connection:
        audit(connection, user["id"], "UPLOAD_IMAGE", "media", filename, {"category": category, "size": len(body)})
    return {"url": f"/uploads/{category}/{filename}"}


@app.post("/api/auth/login")
def login(data: LoginInput):
    with db_cursor() as connection:
        user = row_to_dict(connection.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (data.email.strip(),)).fetchone())
        if not user or not user["active"] or not verify_password(data.password, user["password_hash"]):
            raise HTTPException(401, "Email atau password salah")
        audit(connection, user["id"], "LOGIN", "auth")
        public = {key: user[key] for key in ("id", "name", "email", "phone", "role", "active")}
        return {"access_token": create_token(public), "token_type": "bearer", "user": public}


@app.get("/api/auth/me")
def me(user=Depends(current_user)):
    return user


@app.get("/api/dashboard")
def dashboard(user=Depends(current_user)):
    with db_cursor() as connection:
        units = [row_to_dict(row) for row in connection.execute("SELECT * FROM units ORDER BY updated_at DESC")]
        active = [unit for unit in units if unit["status"] not in ("SOLD_DELIVERED", "REJECTED")]
        sold = [unit for unit in units if unit["status"] == "SOLD_DELIVERED"]
        return {
            "metrics": {"active": len(active), "repair": sum(u["status"] == "IN_REPAIR" for u in units), "published": sum(u["status"] == "PUBLISHED" for u in units), "sold": len(sold), "revenue": sum(u["sell_price"] for u in sold) if user["role"] == "ROLE_OWNER" else None, "profit": sum(u["sell_price"] - u["buy_price"] - u["repair_cost"] for u in sold) if user["role"] == "ROLE_OWNER" else None},
            "pipeline": {status: sum(u["status"] == status for u in units) for status in ("CHECKER_ASSIGNED", "REPORT_SUBMITTED", "IN_REPAIR", "READY_TO_SELL", "PUBLISHED")},
            "recent_units": units[:4],
            "upcoming_events": [row_to_dict(row) for row in connection.execute("SELECT e.*,u.brand,u.model FROM events e LEFT JOIN units u ON u.id=e.unit_id ORDER BY starts_at LIMIT 5")],
        }


@app.get("/api/units")
def list_units(status: str | None = None, search: str = "", user=Depends(current_user)):
    where, values = [], []
    if status:
        where.append("u.status=?"); values.append(status)
    if search:
        where.append("lower(u.brand||' '||u.model||' '||u.plate||' '||u.id) LIKE ?"); values.append(f"%{search.lower()}%")
    clause = " WHERE " + " AND ".join(where) if where else ""
    with db_cursor() as connection:
        return [row_to_dict(row) for row in connection.execute(f"SELECT u.*,c.name assigned_checker_name FROM units u LEFT JOIN users c ON c.id=u.assigned_checker_id{clause} ORDER BY u.updated_at DESC", values)]


@app.post("/api/units", status_code=201)
def create_unit(data: UnitCreate, user=Depends(allow(ROLE_BUYER))):
    with db_cursor() as connection:
        last = connection.execute("SELECT id FROM units ORDER BY id DESC LIMIT 1").fetchone()
        sequence = int(last["id"].split("-")[-1]) + 1 if last else 1
        unit_id = f"LBA-2026-{sequence:04d}"
        now = now_iso()
        try:
            connection.execute("""INSERT INTO units(id,brand,model,year,color,plate,transmission,km,vin,engine_number,source,seller,seller_phone,location,offer_price,target_price,source_photos,status,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (unit_id,data.brand,data.model,data.year,data.color,data.plate.upper(),data.transmission,data.km,data.vin,data.engine_number,data.source,data.seller,data.seller_phone,data.location,data.offer_price,data.target_price,json.dumps([data.cover_photo]),"SOURCED",user["id"],now,now))
        except Exception as exc:
            if "UNIQUE" in str(exc): raise HTTPException(409, "Nomor polisi sudah terdaftar")
            raise
        connection.execute("INSERT INTO documents(unit_id,updated_at) VALUES(?,?)", (unit_id,now))
        audit(connection,user["id"],"CREATE","unit",unit_id,data.model_dump())
        notify_role(connection, ROLE_INSPECTOR_LEAD, f"Unit {unit_id} menunggu Initial QC.", "INITIAL_QC_REQUIRED", unit_id)
        return fetch_unit(connection, unit_id)


@app.get("/api/units/{unit_id}")
def unit_detail(unit_id: str, user=Depends(current_user)):
    with db_cursor() as connection: return fetch_unit(connection, unit_id)


@app.post("/api/units/{unit_id}/assign")
def assign_checker(unit_id: str, data: AssignmentInput, user=Depends(allow(ROLE_INSPECTOR_LEAD))):
    with db_cursor() as connection:
        checker = connection.execute("SELECT id FROM users WHERE id=? AND role=? AND active=1", (data.checker_id,ROLE_FIELD_CHECKER)).fetchone()
        if not checker: raise HTTPException(422, "Field checker tidak valid")
        unit = connection.execute("SELECT * FROM units WHERE id=?",(unit_id,)).fetchone()
        require_status(unit, "LEGAL_PRECHECK")
        connection.execute("UPDATE units SET assigned_checker_id=?,status='CHECKER_ASSIGNED',updated_at=? WHERE id=?",(data.checker_id,now_iso(),unit_id))
        audit(connection,user["id"],"ASSIGN_CHECKER","unit",unit_id,{"checker_id":data.checker_id})
        return fetch_unit(connection,unit_id)


@app.post("/api/units/{unit_id}/initial-qc")
def initial_qc(unit_id: str, data: InitialQCInput, user=Depends(allow(ROLE_INSPECTOR_LEAD))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        require_status(unit, "SOURCED")
        now = now_iso()
        connection.execute(
            "INSERT INTO initial_qc(unit_id,approved,notes,reviewed_by,reviewed_at) VALUES(?,?,?,?,?)",
            (unit_id, int(data.approved), data.notes, user["id"], now),
        )
        status = "INITIAL_QC" if data.approved else "REJECTED"
        connection.execute("UPDATE units SET status=?,rejection_reason=?,updated_at=? WHERE id=?", (status, None if data.approved else data.notes, now, unit_id))
        audit(connection, user["id"], "INITIAL_QC", "unit", unit_id, data.model_dump())
        if data.approved:
            notify_role(connection, ROLE_LEGAL, f"Unit {unit_id} menunggu pemeriksaan legal awal.", "LEGAL_PRECHECK_REQUIRED", unit_id)
        return fetch_unit(connection, unit_id)


@app.post("/api/units/{unit_id}/legal-precheck")
def legal_precheck(unit_id: str, data: LegalPrecheckInput, user=Depends(allow(ROLE_LEGAL))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        require_status(unit, "INITIAL_QC")
        checks = [data.stnk_available, data.bpkb_available, data.vin_match, data.engine_match, data.tax_checked]
        if not all(checks):
            raise HTTPException(422, "Semua pemeriksaan legal wajib lolos sebelum unit dapat diteruskan")
        now = now_iso()
        connection.execute(
            """INSERT INTO legal_prechecks(unit_id,stnk_available,bpkb_available,vin_match,engine_match,tax_checked,notes,approved_by,approved_at)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (unit_id, *[int(value) for value in checks], data.notes, user["id"], now),
        )
        connection.execute("UPDATE units SET status='LEGAL_PRECHECK',updated_at=? WHERE id=?", (now, unit_id))
        audit(connection, user["id"], "LEGAL_PRECHECK", "unit", unit_id, data.model_dump())
        notify_role(connection, ROLE_INSPECTOR_LEAD, f"Legal unit {unit_id} sudah lolos. Silakan tugaskan checker.", "CHECKER_ASSIGNMENT_REQUIRED", unit_id)
        return fetch_unit(connection, unit_id)


@app.post("/api/units/{unit_id}/inspection")
def submit_inspection(unit_id: str, data: InspectionInput, user=Depends(allow(ROLE_FIELD_CHECKER, ROLE_INSPECTOR_LEAD))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?",(unit_id,)).fetchone()
        require_status(unit, "CHECKER_ASSIGNED")
        if user["role"] == ROLE_FIELD_CHECKER and unit["assigned_checker_id"] != user["id"]: raise HTTPException(403,"Unit ini bukan tugas Anda")
        connection.execute("""INSERT INTO inspections(unit_id,checker_id,body_score,major_accident,flood,engine_condition,oil_condition,suspension_condition,tax_status,notes,photos,submitted_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(unit_id) DO UPDATE SET checker_id=excluded.checker_id,body_score=excluded.body_score,major_accident=excluded.major_accident,flood=excluded.flood,engine_condition=excluded.engine_condition,oil_condition=excluded.oil_condition,suspension_condition=excluded.suspension_condition,tax_status=excluded.tax_status,notes=excluded.notes,photos=excluded.photos,submitted_at=excluded.submitted_at""",(unit_id,user["id"],data.body_score,int(data.major_accident),int(data.flood),data.engine_condition,data.oil_condition,data.suspension_condition,data.tax_status,data.notes,json.dumps(data.photos),now_iso()))
        connection.execute("UPDATE units SET status='REPORT_SUBMITTED',updated_at=? WHERE id=?",(now_iso(),unit_id))
        audit(connection,user["id"],"SUBMIT_INSPECTION","unit",unit_id,{"body_score":data.body_score})
        notify_role(connection, ROLE_HOD, f"Laporan inspeksi unit {unit_id} menunggu keputusan HOD.", "HOD_APPROVAL_REQUIRED", unit_id)
        return fetch_unit(connection,unit_id)


@app.post("/api/units/{unit_id}/purchase-decision")
def purchase_decision(unit_id: str, data: PurchaseDecisionInput, user=Depends(allow(ROLE_HOD))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?",(unit_id,)).fetchone()
        require_status(unit, "REPORT_SUBMITTED")
        if data.decision == "DEAL":
            if data.final_price <= 0: raise HTTPException(422,"Harga deal wajib diisi")
            connection.execute("UPDATE units SET status='HOD_APPROVED',buy_price=?,rejection_reason=NULL,updated_at=? WHERE id=?",(data.final_price,now_iso(),unit_id))
            notify_role(connection, ROLE_BUYER, f"Pembelian unit {unit_id} disetujui HOD. Buat voucher pembayaran.", "PAYMENT_APPROVAL_REQUIRED", unit_id)
        else:
            if not data.rejection_reason.strip(): raise HTTPException(422,"Alasan penolakan wajib diisi")
            connection.execute("UPDATE units SET status='REJECTED',rejection_reason=?,updated_at=? WHERE id=?",(data.rejection_reason,now_iso(),unit_id))
        audit(connection,user["id"],data.decision,"purchase",unit_id,data.model_dump())
        return fetch_unit(connection,unit_id)


@app.post("/api/units/{unit_id}/payment-request")
def payment_request(unit_id: str, data: PaymentRequestInput, user=Depends(allow(ROLE_BUYER))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        require_status(unit, "HOD_APPROVED")
        if data.amount != unit["buy_price"]:
            raise HTTPException(422, "Nominal voucher harus sama dengan harga yang disetujui HOD")
        now = now_iso()
        try:
            connection.execute(
                "INSERT INTO payments(unit_id,voucher_number,amount,method,requested_by,requested_at) VALUES(?,?,?,?,?,?)",
                (unit_id, data.voucher_number, data.amount, data.method, user["id"], now),
            )
        except Exception as exc:
            if "UNIQUE" in str(exc):
                raise HTTPException(409, "Nomor voucher sudah digunakan")
            raise
        connection.execute("UPDATE units SET status='PAYMENT_PENDING',updated_at=? WHERE id=?", (now, unit_id))
        audit(connection, user["id"], "CREATE_PAYMENT_VOUCHER", "unit", unit_id, data.model_dump())
        return fetch_unit(connection, unit_id)


@app.post("/api/units/{unit_id}/payment-confirm")
def payment_confirm(unit_id: str, data: PaymentConfirmInput, user=Depends(allow(ROLE_BUYER))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        require_status(unit, "PAYMENT_PENDING")
        if not data.proof_url.startswith("/uploads/payment/"):
            raise HTTPException(422, "Bukti pembayaran wajib diunggah melalui aplikasi")
        now = now_iso()
        connection.execute("UPDATE payments SET proof_url=?,confirmed_by=?,paid_at=? WHERE unit_id=?", (data.proof_url, user["id"], data.paid_at or now, unit_id))
        connection.execute("UPDATE units SET status='PURCHASED_PAID',updated_at=? WHERE id=?", (now, unit_id))
        audit(connection, user["id"], "CONFIRM_PAYMENT", "unit", unit_id, {"proof_url": data.proof_url})
        notify_role(connection, ROLE_REPAIR_PIC, f"Pembayaran unit {unit_id} selesai. Konfirmasi serah-terima fisik.", "REPAIR_HANDOVER_REQUIRED", unit_id)
        return fetch_unit(connection, unit_id)


@app.post("/api/units/{unit_id}/repair-handover")
def repair_handover(unit_id: str, data: RepairHandoverInput, user=Depends(allow(ROLE_REPAIR_PIC))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        require_status(unit, "PURCHASED_PAID")
        now = now_iso()
        connection.execute(
            """INSERT INTO repairs(unit_id,categories,vendor,stage,estimated_cost,actual_cost,progress,target_date,notes,updated_by,updated_at,handover_at,handover_odometer,handover_notes)
               VALUES(?, '[]', '', 'SERAH_TERIMA', 0, 0, 0, NULL, '', ?, ?, ?, ?, ?)
               ON CONFLICT(unit_id) DO UPDATE SET handover_at=excluded.handover_at,handover_odometer=excluded.handover_odometer,handover_notes=excluded.handover_notes,updated_by=excluded.updated_by,updated_at=excluded.updated_at""",
            (unit_id, user["id"], now, now, data.odometer, data.notes),
        )
        connection.execute("UPDATE units SET status='REPAIR_HANDOVER',km=?,updated_at=? WHERE id=?", (data.odometer, now, unit_id))
        audit(connection, user["id"], "REPAIR_HANDOVER", "unit", unit_id, data.model_dump())
        return fetch_unit(connection, unit_id)


@app.put("/api/units/{unit_id}/repair")
def update_repair(unit_id: str, data: RepairInput, user=Depends(allow(ROLE_REPAIR_PIC))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?",(unit_id,)).fetchone()
        require_status(unit, "REPAIR_HANDOVER", "IN_REPAIR")
        if not data.work_items:
            raise HTTPException(422, "Minimal satu pekerjaan repair wajib diisi")
        work_items = [item.model_dump() for item in data.work_items]
        progress = round(sum(item["progress"] for item in work_items) / len(work_items))
        estimated = sum(item["estimated_cost"] for item in work_items)
        actual = sum(item["actual_cost"] for item in work_items)
        categories = sorted({item["category"] for item in work_items})
        if progress == 100 and (not data.before_photos or not data.after_photos):
            raise HTTPException(422, "Foto before dan after wajib sebelum mengajukan Repair QC")
        connection.execute("""UPDATE repairs SET categories=?,vendor=?,stage=?,estimated_cost=?,actual_cost=?,progress=?,target_date=?,notes=?,work_items=?,before_photos=?,after_photos=?,qc_status='PENDING',updated_by=?,updated_at=? WHERE unit_id=?""",(json.dumps(categories),data.vendor,data.stage,estimated,actual,progress,data.target_date,data.notes,json.dumps(work_items),json.dumps(data.before_photos),json.dumps(data.after_photos),user["id"],now_iso(),unit_id))
        status = "REPAIR_QC" if progress == 100 else "IN_REPAIR"
        connection.execute("UPDATE units SET status=?,repair_cost=?,progress=?,updated_at=? WHERE id=?",(status,actual,progress,now_iso(),unit_id))
        audit(connection,user["id"],"UPDATE_REPAIR","unit",unit_id,{"progress":progress,"work_items":work_items})
        if status == "REPAIR_QC":
            notify_role(connection, ROLE_HOD, f"Repair unit {unit_id} selesai dan menunggu Repair QC.", "REPAIR_QC_REQUIRED", unit_id)
        return fetch_unit(connection,unit_id)


@app.post("/api/units/{unit_id}/repair-qc")
def repair_qc(unit_id: str, data: ApprovalInput, user=Depends(allow(ROLE_HOD))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        require_status(unit, "REPAIR_QC")
        repair = connection.execute("SELECT * FROM repairs WHERE unit_id=?", (unit_id,)).fetchone()
        if not repair or not json.loads(repair["before_photos"]) or not json.loads(repair["after_photos"]):
            raise HTTPException(422, "Foto before dan after repair belum lengkap")
        now = now_iso()
        connection.execute("UPDATE repairs SET qc_status=?,qc_notes=?,qc_by=?,qc_at=? WHERE unit_id=?", ("PASSED" if data.approved else "REJECTED", data.notes, user["id"], now, unit_id))
        status = "DOCUMENT_QC" if data.approved else "IN_REPAIR"
        connection.execute("UPDATE units SET status=?,updated_at=? WHERE id=?", (status, now, unit_id))
        audit(connection, user["id"], "REPAIR_QC", "unit", unit_id, data.model_dump())
        if data.approved:
            notify_role(connection, ROLE_LEGAL, f"Repair QC unit {unit_id} lulus. Document QC perlu diselesaikan.", "DOCUMENT_QC_REQUIRED", unit_id)
        return fetch_unit(connection, unit_id)


@app.put("/api/units/{unit_id}/documents")
def update_documents(unit_id: str, data: DocumentInput, user=Depends(allow(ROLE_LEGAL))):
    ready = data.stnk_status == "ADA_ASLI" and data.bpkb_status == "ADA_ASLI" and data.invoice_status == "LENGKAP" and data.receipt_available and data.owner_id_copy
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?",(unit_id,)).fetchone()
        require_status(unit, "DOCUMENT_QC")
        now = now_iso()
        connection.execute("""INSERT INTO documents(unit_id,stnk_status,tax_due,plate_due,bpkb_status,bpkb_number,invoice_status,receipt_available,owner_id_copy,items,ready_for_sale,updated_by,updated_at,qc_by,qc_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(unit_id) DO UPDATE SET stnk_status=excluded.stnk_status,tax_due=excluded.tax_due,plate_due=excluded.plate_due,bpkb_status=excluded.bpkb_status,bpkb_number=excluded.bpkb_number,invoice_status=excluded.invoice_status,receipt_available=excluded.receipt_available,owner_id_copy=excluded.owner_id_copy,items=excluded.items,ready_for_sale=excluded.ready_for_sale,updated_by=excluded.updated_by,updated_at=excluded.updated_at,qc_by=excluded.qc_by,qc_at=excluded.qc_at""",(unit_id,data.stnk_status,data.tax_due,data.plate_due,data.bpkb_status,data.bpkb_number,data.invoice_status,int(data.receipt_available),int(data.owner_id_copy),json.dumps(data.items),int(ready),user["id"],now,user["id"],now))
        connection.execute("UPDATE units SET tax_due=?,status=?,updated_at=? WHERE id=?",(data.tax_due,"READY_TO_SELL" if ready else "DOCUMENT_QC",now,unit_id))
        audit(connection,user["id"],"UPDATE_DOCUMENTS","unit",unit_id,{"ready":ready})
        return fetch_unit(connection,unit_id)


@app.get("/api/leads")
def list_leads(user=Depends(allow(ROLE_SALES))):
    with db_cursor() as connection: return [row_to_dict(row) for row in connection.execute("SELECT l.*,u.brand,u.model,u.source_photos FROM leads l LEFT JOIN units u ON u.id=l.unit_id ORDER BY l.updated_at DESC")]


@app.post("/api/leads", status_code=201)
def create_lead(data: LeadCreate, user=Depends(allow(ROLE_SALES))):
    with db_cursor() as connection:
        last=connection.execute("SELECT id FROM leads ORDER BY id DESC LIMIT 1").fetchone(); seq=int(last["id"].split("-")[-1])+1 if last else 1; lead_id=f"LD-{seq:04d}"; now=now_iso()
        connection.execute("INSERT INTO leads(id,name,phone,unit_id,source,status,notes,assigned_to,created_at,updated_at) VALUES(?,?,?,?,?,'NEW',?,?,?,?)",(lead_id,data.name,data.phone,data.unit_id,data.source,data.notes,data.assigned_to or user["id"],now,now))
        audit(connection,user["id"],"CREATE","lead",lead_id,data.model_dump())
        return row_to_dict(connection.execute("SELECT * FROM leads WHERE id=?",(lead_id,)).fetchone())


@app.patch("/api/leads/{lead_id}/status")
def update_lead_status(lead_id: str, data: LeadStatusInput, user=Depends(allow(ROLE_SALES))):
    with db_cursor() as connection:
        if not connection.execute("SELECT id FROM leads WHERE id=?",(lead_id,)).fetchone(): raise HTTPException(404,"Lead tidak ditemukan")
        if data.notes is None: connection.execute("UPDATE leads SET status=?,updated_at=? WHERE id=?",(data.status,now_iso(),lead_id))
        else: connection.execute("UPDATE leads SET status=?,notes=?,updated_at=? WHERE id=?",(data.status,data.notes,now_iso(),lead_id))
        audit(connection,user["id"],"UPDATE_STATUS","lead",lead_id,{"status":data.status})
        return row_to_dict(connection.execute("SELECT * FROM leads WHERE id=?",(lead_id,)).fetchone())


@app.get("/api/events")
def list_events(user=Depends(current_user)):
    with db_cursor() as connection: return [row_to_dict(row) for row in connection.execute("SELECT e.*,u.brand,u.model,a.name assigned_name FROM events e LEFT JOIN units u ON u.id=e.unit_id LEFT JOIN users a ON a.id=e.assigned_to ORDER BY starts_at")]


@app.post("/api/events", status_code=201)
def create_event(data: EventCreate, user=Depends(current_user)):
    with db_cursor() as connection:
        cursor=connection.execute("INSERT INTO events(title,event_type,starts_at,unit_id,assigned_to,notes,created_by,created_at) VALUES(?,?,?,?,?,?,?,?)",(data.title,data.event_type,data.starts_at,data.unit_id,data.assigned_to,data.notes,user["id"],now_iso()))
        audit(connection,user["id"],"CREATE","event",cursor.lastrowid,data.model_dump())
        return row_to_dict(connection.execute("SELECT * FROM events WHERE id=?",(cursor.lastrowid,)).fetchone())


@app.post("/api/sales", status_code=201)
def create_sale(data: SaleCreate, user=Depends(allow(ROLE_SALES))):
    with db_cursor() as connection:
        unit=connection.execute("SELECT * FROM units WHERE id=?",(data.unit_id,)).fetchone()
        if not unit: raise HTTPException(404,"Unit tidak ditemukan")
        if unit["status"] not in ("READY_TO_SELL","PUBLISHED"): raise HTTPException(409,"Unit belum siap dijual")
        documents = connection.execute("SELECT ready_for_sale FROM documents WHERE unit_id=?", (data.unit_id,)).fetchone()
        if not documents or not documents["ready_for_sale"]: raise HTTPException(409,"Document QC belum lulus")
        if data.payment_scheme == "CREDIT" and (not data.leasing_vendor or not data.tenor_months):
            raise HTTPException(422, "Vendor leasing dan tenor wajib untuk transaksi kredit")
        now = now_iso()
        cursor=connection.execute("""INSERT INTO sales(unit_id,buyer_name,buyer_phone,buyer_nik,buyer_address,payment_scheme,leasing_vendor,tenor_months,down_payment,final_price,delivered_at,created_by,created_at,status,booked_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,'BOOKED',?)""",(data.unit_id,data.buyer_name,data.buyer_phone,data.buyer_nik,data.buyer_address,data.payment_scheme,data.leasing_vendor,data.tenor_months,data.down_payment,data.final_price,None,user["id"],now,now))
        connection.execute("UPDATE units SET status='BOOKED',sell_price=?,updated_at=? WHERE id=?",(data.final_price,now,data.unit_id))
        audit(connection,user["id"],"CREATE","sale",cursor.lastrowid,data.model_dump())
        return fetch_unit(connection,data.unit_id)


@app.post("/api/sales/{unit_id}/payment-process")
def sale_payment_process(unit_id: str, user=Depends(allow(ROLE_SALES))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        require_status(unit, "BOOKED")
        sale = connection.execute("SELECT * FROM sales WHERE unit_id=?", (unit_id,)).fetchone()
        if not sale: raise HTTPException(404, "Booking tidak ditemukan")
        status = "SURVEY_FINANCE" if sale["payment_scheme"] == "CREDIT" else "CASH_CONFIRMED"
        connection.execute("UPDATE sales SET status=? WHERE unit_id=?", (status, unit_id))
        connection.execute("UPDATE units SET status=?,updated_at=? WHERE id=?", (status, now_iso(), unit_id))
        audit(connection, user["id"], "START_PAYMENT_PROCESS", "sale", unit_id, {"status": status})
        return fetch_unit(connection, unit_id)


@app.post("/api/sales/{unit_id}/survey-complete")
def survey_finance_complete(unit_id: str, user=Depends(allow(ROLE_SALES))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        require_status(unit, "SURVEY_FINANCE")
        connection.execute("UPDATE sales SET status='FINANCE_PROCESS' WHERE unit_id=?", (unit_id,))
        connection.execute("UPDATE units SET status='FINANCE_PROCESS',updated_at=? WHERE id=?", (now_iso(), unit_id))
        audit(connection, user["id"], "COMPLETE_FINANCE_SURVEY", "sale", unit_id)
        notify_role(connection, ROLE_SALES, f"Survey finance unit {unit_id} selesai dan menunggu keputusan leasing.", "FINANCE_APPROVAL_REQUIRED", unit_id)
        return fetch_unit(connection, unit_id)


@app.post("/api/sales/{unit_id}/finance-approval")
def finance_approval(unit_id: str, data: FinanceApprovalInput, user=Depends(allow(ROLE_SALES))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        require_status(unit, "FINANCE_PROCESS")
        now = now_iso()
        status = "FINANCE_APPROVED" if data.approved else "BOOKED"
        connection.execute("UPDATE sales SET status=?,finance_reference=?,finance_approved_at=?,notes=? WHERE unit_id=?", (status, data.reference, now if data.approved else None, data.notes, unit_id))
        connection.execute("UPDATE units SET status=?,updated_at=? WHERE id=?", (status, now, unit_id))
        audit(connection, user["id"], "FINANCE_APPROVAL", "sale", unit_id, data.model_dump())
        return fetch_unit(connection, unit_id)


@app.post("/api/sales/{unit_id}/deal")
def mark_deal(unit_id: str, user=Depends(allow(ROLE_SALES))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        require_status(unit, "FINANCE_APPROVED", "CASH_CONFIRMED")
        now = now_iso()
        connection.execute("UPDATE sales SET status='DEAL',deal_at=? WHERE unit_id=?", (now, unit_id))
        connection.execute("UPDATE units SET status='DEAL',updated_at=? WHERE id=?", (now, unit_id))
        audit(connection, user["id"], "DEAL", "sale", unit_id)
        return fetch_unit(connection, unit_id)


@app.post("/api/sales/{unit_id}/schedule-delivery")
def schedule_delivery(unit_id: str, data: DeliveryScheduleInput, user=Depends(allow(ROLE_SALES))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        require_status(unit, "DEAL")
        connection.execute("UPDATE sales SET status='DELIVERY_SCHEDULED',delivery_scheduled_at=?,notes=? WHERE unit_id=?", (data.scheduled_at, data.notes, unit_id))
        connection.execute("UPDATE units SET status='DELIVERY_SCHEDULED',updated_at=? WHERE id=?", (now_iso(), unit_id))
        audit(connection, user["id"], "SCHEDULE_DELIVERY", "sale", unit_id, data.model_dump())
        return fetch_unit(connection, unit_id)


@app.post("/api/sales/{unit_id}/complete-delivery")
def complete_delivery(unit_id: str, data: DeliveryCompleteInput, user=Depends(allow(ROLE_SALES))):
    with db_cursor() as connection:
        unit = connection.execute("SELECT * FROM units WHERE id=?", (unit_id,)).fetchone()
        require_status(unit, "DELIVERY_SCHEDULED")
        now = now_iso()
        connection.execute("UPDATE sales SET status='SOLD_DELIVERED',delivered_at=?,delivery_completed_at=?,notes=? WHERE unit_id=?", (now, now, data.notes, unit_id))
        connection.execute("UPDATE units SET status='SOLD_DELIVERED',updated_at=? WHERE id=?", (now, unit_id))
        audit(connection, user["id"], "COMPLETE_DELIVERY", "sale", unit_id, data.model_dump())
        return fetch_unit(connection, unit_id)


@app.put("/api/units/{unit_id}/listing")
def update_listing(unit_id: str, data: ListingInput, user=Depends(allow(ROLE_SALES))):
    with db_cursor() as connection:
        unit=connection.execute("SELECT * FROM units WHERE id=?",(unit_id,)).fetchone()
        if not unit: raise HTTPException(404,"Unit tidak ditemukan")
        if unit["status"] not in ("READY_TO_SELL","PUBLISHED"): raise HTTPException(409,"Unit belum siap dipublikasikan")
        documents=connection.execute("SELECT ready_for_sale FROM documents WHERE unit_id=?",(unit_id,)).fetchone()
        if not documents or not documents["ready_for_sale"]: raise HTTPException(409,"Document QC belum lulus")
        published_at=now_iso() if data.publish else None
        connection.execute("""INSERT INTO listings(unit_id,media_items,video_url,cash_price,credit_price,description,channels,published_at,updated_by,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(unit_id) DO UPDATE SET media_items=excluded.media_items,video_url=excluded.video_url,cash_price=excluded.cash_price,credit_price=excluded.credit_price,description=excluded.description,channels=excluded.channels,published_at=excluded.published_at,updated_by=excluded.updated_by,updated_at=excluded.updated_at""",(unit_id,json.dumps(data.media_items),data.video_url,data.cash_price,data.credit_price,data.description,json.dumps(data.channels),published_at,user["id"],now_iso()))
        connection.execute("UPDATE units SET sell_price=?,status=?,updated_at=? WHERE id=?",(data.cash_price,"PUBLISHED" if data.publish else unit["status"],now_iso(),unit_id))
        audit(connection,user["id"],"PUBLISH" if data.publish else "UPDATE_LISTING","unit",unit_id,{"channels":data.channels})
        return fetch_unit(connection,unit_id)


@app.post("/api/credit-simulation")
def credit_simulation(data: CreditSimulationInput, user=Depends(allow(ROLE_SALES))):
    principal=max(0,data.otr_price-data.total_down_payment)
    interest=principal*(data.annual_interest_rate/100)*(data.tenor_months/12)
    financed_total=round(principal+interest+data.admin_fee+data.insurance_fee)
    monthly=round(financed_total/data.tenor_months)
    return {"principal":principal,"total_interest":round(interest),"financed_total":financed_total,"monthly_installment":monthly,"tenor_months":data.tenor_months,"total_down_payment":data.total_down_payment}


@app.post("/api/units/{unit_id}/greeting")
def save_greeting(unit_id: str, data: GreetingInput, user=Depends(allow(ROLE_SALES))):
    with db_cursor() as connection:
        unit=connection.execute("SELECT * FROM units WHERE id=?",(unit_id,)).fetchone()
        if not unit: raise HTTPException(404,"Unit tidak ditemukan")
        if unit["status"] != "SOLD_DELIVERED": raise HTTPException(409,"Greeting hanya tersedia setelah delivery")
        if data.media_url and not data.consent: raise HTTPException(422,"Persetujuan konsumen wajib untuk menyimpan media")
        connection.execute("""INSERT INTO greetings(unit_id,media_url,rating,consent,notes,created_by,created_at) VALUES(?,?,?,?,?,?,?) ON CONFLICT(unit_id) DO UPDATE SET media_url=excluded.media_url,rating=excluded.rating,consent=excluded.consent,notes=excluded.notes,created_by=excluded.created_by,created_at=excluded.created_at""",(unit_id,data.media_url,data.rating,int(data.consent),data.notes,user["id"],now_iso()))
        audit(connection,user["id"],"SAVE_GREETING","unit",unit_id,{"rating":data.rating,"consent":data.consent})
        return fetch_unit(connection,unit_id)


@app.get("/api/sales/{unit_id}/document/{document_type}", response_class=HTMLResponse)
def transaction_document(unit_id: str, document_type: str, user=Depends(allow(ROLE_SALES))):
    if document_type not in ("spk","receipt","bastk"): raise HTTPException(404,"Jenis dokumen tidak tersedia")
    labels={"spk":"SURAT PEMESANAN KENDARAAN","receipt":"KWITANSI PELUNASAN","bastk":"BERITA ACARA SERAH TERIMA KENDARAAN"}
    with db_cursor() as connection:
        row=connection.execute("""SELECT s.*,u.brand,u.model,u.year,u.plate,u.id unit_code FROM sales s JOIN units u ON u.id=s.unit_id WHERE s.unit_id=?""",(unit_id,)).fetchone()
        if not row: raise HTTPException(404,"Transaksi tidak ditemukan")
        sale=row_to_dict(row)
    title=labels[document_type]
    return HTMLResponse(f"""<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>body{{font:14px Arial;color:#17201e;max-width:760px;margin:48px auto;padding:24px}}h1{{font:26px Georgia;text-align:center;margin-bottom:40px}}table{{width:100%;border-collapse:collapse}}td{{padding:10px;border-bottom:1px solid #ddd}}td:first-child{{color:#6f7976;width:35%}}.sign{{margin-top:80px;text-align:right}}@media print{{button{{display:none}}body{{margin:0}}}}</style></head><body><button onclick='print()'>Cetak / Simpan PDF</button><h1>{title}</h1><table><tr><td>Nomor unit</td><td>{escape(sale['unit_code'])}</td></tr><tr><td>Kendaraan</td><td>{escape(sale['brand'])} {escape(sale['model'])} ({sale['year']})</td></tr><tr><td>Nomor polisi</td><td>{escape(sale['plate'])}</td></tr><tr><td>Pembeli</td><td>{escape(sale['buyer_name'])}</td></tr><tr><td>Nomor WhatsApp</td><td>{escape(sale['buyer_phone'])}</td></tr><tr><td>Skema pembayaran</td><td>{escape(sale['payment_scheme'])}</td></tr><tr><td>Harga final</td><td>Rp {sale['final_price']:,}</td></tr><tr><td>Tanggal delivery</td><td>{escape(sale['delivered_at'] or '-')}</td></tr></table><div class='sign'>Jakarta, __________________<br><br><br><strong>LB AUTO</strong></div></body></html>""")


@app.get("/api/reports/financial")
def financial_report(user=Depends(allow())):
    with db_cursor() as connection:
        sold=[row_to_dict(row) for row in connection.execute("SELECT * FROM units WHERE status='SOLD_DELIVERED' ORDER BY updated_at DESC")]
        rows=[]
        for unit in sold:
            hpp=unit["buy_price"]+unit["repair_cost"]; rows.append({**unit,"hpp":hpp,"profit":unit["sell_price"]-hpp,"margin":round((unit["sell_price"]-hpp)/unit["sell_price"]*100,2) if unit["sell_price"] else 0})
        return {"revenue":sum(x["sell_price"] for x in rows),"hpp":sum(x["hpp"] for x in rows),"profit":sum(x["profit"] for x in rows),"units":rows}


@app.get("/api/reports/export/pdf")
def export_report_pdf(request: Request, user=Depends(allow())):
    with db_cursor() as connection:
        data = collect_report_data(connection)
        audit(connection, user["id"], "EXPORT_PDF", "report", "full-operational")
    output = build_pdf(data, BASE_DIR, str(request.base_url))
    filename = f"LB-AUTO-Laporan-Lengkap-{datetime.now().strftime('%Y%m%d-%H%M')}.pdf"
    return Response(
        output.getvalue(), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/reports/export/excel")
def export_report_excel(request: Request, user=Depends(allow())):
    with db_cursor() as connection:
        data = collect_report_data(connection)
        audit(connection, user["id"], "EXPORT_EXCEL", "report", "full-operational")
    output = build_excel(data, str(request.base_url))
    filename = f"LB-AUTO-Laporan-Lengkap-{datetime.now().strftime('%Y%m%d-%H%M')}.xlsx"
    return Response(
        output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/users")
def list_users(role: str | None = Query(None), user=Depends(current_user)):
    with db_cursor() as connection:
        if role:
            if user["role"] != "ROLE_OWNER" and role != ROLE_FIELD_CHECKER:
                raise HTTPException(403,"Akses daftar user dibatasi")
            rows=connection.execute("SELECT id,name,email,phone,role,active,created_at FROM users WHERE role=? ORDER BY name",(role,))
        else:
            if user["role"] != "ROLE_OWNER": raise HTTPException(403,"Akses khusus owner")
            rows=connection.execute("SELECT id,name,email,phone,role,active,created_at FROM users ORDER BY name")
        return [row_to_dict(row) for row in rows]


@app.post("/api/users", status_code=201)
def create_user(data: UserCreate, user=Depends(allow())):
    if data.role not in ROLES: raise HTTPException(422,"Role tidak valid")
    with db_cursor() as connection:
        try: cursor=connection.execute("INSERT INTO users(name,email,password_hash,role,phone,active,created_at) VALUES(?,?,?,?,?,1,?)",(data.name,data.email.lower(),hash_password(data.password),data.role,data.phone,now_iso()))
        except Exception as exc:
            if "UNIQUE" in str(exc): raise HTTPException(409,"Email sudah digunakan")
            raise
        audit(connection,user["id"],"CREATE","user",cursor.lastrowid,{"email":data.email,"role":data.role})
        return row_to_dict(connection.execute("SELECT id,name,email,phone,role,active,created_at FROM users WHERE id=?",(cursor.lastrowid,)).fetchone())


@app.patch("/api/users/{user_id}/contact")
def update_user_contact(user_id: int, data: UserContactInput, user=Depends(allow())):
    with db_cursor() as connection:
        if not connection.execute("SELECT id FROM users WHERE id=?", (user_id,)).fetchone():
            raise HTTPException(404, "User tidak ditemukan")
        connection.execute("UPDATE users SET phone=? WHERE id=?", (data.phone.strip(), user_id))
        audit(connection, user["id"], "UPDATE_CONTACT", "user", user_id, {"phone_configured": bool(data.phone.strip())})
        return {"ok": True}


@app.patch("/api/users/{user_id}/status")
def update_user_status(user_id: int, data: UserStatusInput, user=Depends(allow())):
    if user_id == user["id"] and not data.active: raise HTTPException(422,"Tidak dapat menonaktifkan akun sendiri")
    with db_cursor() as connection:
        connection.execute("UPDATE users SET active=? WHERE id=?",(int(data.active),user_id)); audit(connection,user["id"],"UPDATE_STATUS","user",user_id,{"active":data.active})
        return {"ok":True}


@app.get("/api/audit-logs")
def audit_logs(limit: int = Query(100,le=500), user=Depends(allow())):
    with db_cursor() as connection: return [row_to_dict(row) for row in connection.execute("SELECT a.*,u.name user_name FROM audit_logs a LEFT JOIN users u ON u.id=a.user_id ORDER BY a.id DESC LIMIT ?",(limit,))]


@app.get("/api/notifications")
def notifications(limit: int = Query(50, le=200), user=Depends(allow())):
    with db_cursor() as connection:
        return [row_to_dict(row) for row in connection.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT ?", (limit,))]


app.mount("/assets", StaticFiles(directory=BASE_DIR / "assets"), name="assets")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str):
    if path == "api" or path.startswith("api/"):
        raise HTTPException(404, "Endpoint API tidak ditemukan")
    requested = BASE_DIR / path
    if path and requested.is_file() and BASE_DIR in requested.resolve().parents:
        return FileResponse(requested)
    return FileResponse(BASE_DIR / "index.html")
