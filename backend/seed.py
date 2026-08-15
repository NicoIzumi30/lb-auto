import json

from .auth import (
    ROLE_BUYER, ROLE_FIELD_CHECKER, ROLE_HOD, ROLE_INSPECTOR_LEAD, ROLE_LEGAL,
    ROLE_OWNER, ROLE_REPAIR_PIC, ROLE_SALES, hash_password,
)
from .database import db_cursor, init_db, now_iso


DEMO_PASSWORD = "LBAuto123!"


def seed_database(force=False):
    init_db()
    with db_cursor() as connection:
        if force:
            for table in ("notifications", "audit_logs", "greetings", "listings", "sales", "events", "leads", "payments", "documents", "repairs", "inspections", "legal_prechecks", "initial_qc", "units", "users"):
                connection.execute(f"DELETE FROM {table}")
        now = now_iso()
        users = [
            ("Owner LB AUTO", "owner@lbauto.id", ROLE_OWNER),
            ("Krisna Aditya", "krisna@lbauto.id", ROLE_BUYER),
            ("Ciprut", "ciprut@lbauto.id", ROLE_INSPECTOR_LEAD),
            ("Rendi Checker", "checker@lbauto.id", ROLE_FIELD_CHECKER),
            ("Legal Officer", "legal@lbauto.id", ROLE_LEGAL),
            ("Head of Department", "hod@lbauto.id", ROLE_HOD),
            ("Workshop Manager", "workshop@lbauto.id", ROLE_REPAIR_PIC),
            ("Febi Sales", "sales@lbauto.id", ROLE_SALES),
        ]
        for name, email, role in users:
            if not connection.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
                connection.execute("INSERT INTO users(name,email,password_hash,role,active,created_at) VALUES(?,?,?,?,1,?)", (name,email,hash_password(DEMO_PASSWORD),role,now))
        ids = {row["email"]: row["id"] for row in connection.execute("SELECT id,email FROM users")}
        if connection.execute("SELECT COUNT(*) FROM units").fetchone()[0]:
            connection.execute("""UPDATE documents SET stnk_status='ADA_ASLI',bpkb_status='ADA_ASLI',invoice_status='LENGKAP',receipt_available=1,owner_id_copy=1,ready_for_sale=1
                                  WHERE updated_by IS NULL AND unit_id IN (SELECT id FROM units WHERE status IN ('READY_TO_SELL','PUBLISHED','SOLD_DELIVERED'))""")
            connection.execute("""UPDATE sales SET status='SOLD_DELIVERED',booked_at=COALESCE(booked_at,created_at),delivery_completed_at=COALESCE(delivery_completed_at,delivered_at)
                                  WHERE unit_id IN (SELECT id FROM units WHERE status='SOLD_DELIVERED')""")
            return
        units = [
            ("LBA-2026-0089","Toyota","Fortuner 2.8 VRZ GR",2023,"Phantom Brown","B 1728 UJE","AT",18420,"MHKBA3FS0PK100089","2GDFTV0089","Showroom Mitra","Ardiansyah","081288412370","Jakarta Selatan",585000000,570000000,568000000,8500000,629000000,"IN_REPAIR",ids["checker@lbauto.id"],"2026-09-03",72),
            ("LBA-2026-0088","Mercedes-Benz","C200 Avantgarde",2021,"Obsidian Black","B 912 LBS","AT",27110,"WDD2050422R100088","M2749200088","Perorangan","Michael Tan","08173100448","Tangerang",735000000,715000000,710000000,12500000,795000000,"PUBLISHED",ids["checker@lbauto.id"],"2027-01-17",100),
            ("LBA-2026-0087","BMW","X3 xDrive20i",2022,"Alpine White","B 1189 VAG","AT",22905,"WBA53DP0800100087","B4820A0087","Bursa Mobil","Steven Wijaya","081377509921","Jakarta Utara",885000000,865000000,860000000,6300000,945000000,"READY_TO_SELL",ids["checker@lbauto.id"],"2026-08-29",100),
            ("LBA-2026-0086","Honda","CR-V 1.5 Turbo Prestige",2022,"Platinum White","B 2031 PZX","CVT",31400,"MHRRW1850NJ100086","L15B700086","Perorangan","Diana Putri","08121911840","Bekasi",465000000,455000000,0,0,0,"REPORT_SUBMITTED",ids["checker@lbauto.id"],"2026-11-11",0),
            ("LBA-2026-0085","Lexus","RX 300 Luxury",2020,"Sonic Titanium","B 888 LXR","AT",42300,"JTJBAMCA5L2100085","8ARFTS0085","Agent/Broker","Hendra","08579031114","Bandung",920000000,895000000,0,0,0,"CHECKER_ASSIGNED",ids["checker@lbauto.id"],"2026-10-28",0),
            ("LBA-2026-0084","Toyota","Alphard 2.5 G ATPM",2021,"Black","B 7 LBA","CVT",35220,"JTNGF3DH0M8100084","2ARFE0084","Lelang","PT Lelang Prima","0215551920","Jakarta Barat",990000000,970000000,960000000,18500000,1085000000,"SOLD_DELIVERED",ids["checker@lbauto.id"],"2027-03-10",100),
        ]
        for unit in units:
            connection.execute("""INSERT INTO units(id,brand,model,year,color,plate,transmission,km,vin,engine_number,source,seller,seller_phone,location,offer_price,target_price,buy_price,repair_cost,sell_price,status,assigned_checker_id,tax_due,progress,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (*unit, ids["krisna@lbauto.id"], now, now))
            ready = unit[19] in ("READY_TO_SELL", "PUBLISHED", "SOLD_DELIVERED")
            connection.execute("""INSERT INTO documents(unit_id,tax_due,stnk_status,bpkb_status,invoice_status,receipt_available,owner_id_copy,ready_for_sale,updated_at)
                                  VALUES(?,?,?,?,?,?,?,?,?)""", (unit[0],unit[21],"ADA_ASLI" if ready else "BELUM_DICEK","ADA_ASLI" if ready else "BELUM_DICEK","LENGKAP" if ready else "BELUM_DICEK",int(ready),int(ready),int(ready),now))
        connection.execute("""INSERT INTO inspections(unit_id,checker_id,body_score,major_accident,flood,engine_condition,oil_condition,suspension_condition,tax_status,notes,photos,submitted_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", ("LBA-2026-0086",ids["checker@lbauto.id"],87,0,0,"Halus/Normal","Rembes Tipis","Senyap/Normal","Pajak Hidup","Baret ringan bumper belakang",json.dumps([]),now))
        connection.execute("""INSERT INTO repairs(unit_id,categories,vendor,stage,estimated_cost,actual_cost,progress,target_date,notes,updated_by,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)""", ("LBA-2026-0089",json.dumps(["Cat Body","Bumper Repair"]),"Workshop LB AUTO","TOP_COAT",9000000,8500000,72,"2026-08-14","Final top coat dan polishing",ids["workshop@lbauto.id"],now))
        leads = [("LD-1028","Raka Pratama","081290184773","LBA-2026-0088","Instagram","FOLLOW_UP","Menanyakan paket kredit 36 bulan"),("LD-1027","Susan Lim","0818200883","LBA-2026-0087","OLX","TEST_DRIVE","Test drive Sabtu pukul 11.00"),("LD-1026","Fadli Akbar","08527220193","LBA-2026-0089","Walk-in","NEW","Cari unit diesel tahun muda"),("LD-1025","Kevin Halim","08138877200","LBA-2026-0084","Mobil123","CLOSED","Pembayaran cash")]
        for lead in leads:
            connection.execute("INSERT INTO leads(id,name,phone,unit_id,source,status,notes,assigned_to,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)", (*lead,ids["sales@lbauto.id"],now,now))
        for title,event_type,starts,unit_id,assigned,notes in [
            ("Inspeksi Lexus RX 300","INSPECTION","2026-08-14T09:30:00+07:00","LBA-2026-0085",ids["checker@lbauto.id"],"Lokasi Bandung"),
            ("Target selesai Fortuner","REPAIR","2026-08-14T13:00:00+07:00","LBA-2026-0089",ids["workshop@lbauto.id"],"Final polish"),
            ("Test drive BMW X3","TEST_DRIVE","2026-08-14T16:00:00+07:00","LBA-2026-0087",ids["sales@lbauto.id"],"Susan Lim"),
        ]:
            connection.execute("INSERT INTO events(title,event_type,starts_at,unit_id,assigned_to,notes,created_by,created_at) VALUES(?,?,?,?,?,?,?,?)", (title,event_type,starts,unit_id,assigned,notes,ids["owner@lbauto.id"],now))
        connection.execute("INSERT INTO sales(unit_id,buyer_name,buyer_phone,payment_scheme,final_price,delivered_at,created_by,created_at,status,booked_at,delivery_completed_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)", ("LBA-2026-0084","Kevin Halim","08138877200","CASH",1085000000,"2026-08-08",ids["sales@lbauto.id"],now,"SOLD_DELIVERED",now,"2026-08-08"))


if __name__ == "__main__":
    seed_database(force=True)
    print("Database LB AUTO berhasil dibuat.")
