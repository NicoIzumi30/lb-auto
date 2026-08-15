import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend import database, main
from backend.main import app


PASSWORD = "LBAuto123!"


def auth(client, email):
    response = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


class ApiWorkflowTest(unittest.TestCase):
    def test_complete_workflow_and_rbac(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            database.DB_PATH = Path(temporary_directory) / "test.db"
            main.UPLOAD_DIR = Path(temporary_directory) / "uploads"
            with TestClient(app) as client:
                homepage = client.get("/")
                self.assertEqual(homepage.status_code, 200)
                self.assertIn('/styles.css?v=24', homepage.text)
                self.assertNotIn("cdn.jsdelivr.net", homepage.text)
                self.assertEqual(client.get("/styles.css?v=24").status_code, 200)
                unknown_api = client.get("/api/reports/export/not-available")
                self.assertEqual(unknown_api.status_code, 404)
                self.assertEqual(unknown_api.headers["content-type"], "application/json")

                owner = auth(client, "owner@lbauto.id")
                buyer = auth(client, "krisna@lbauto.id")
                leader = auth(client, "ciprut@lbauto.id")
                checker = auth(client, "checker@lbauto.id")
                legal = auth(client, "legal@lbauto.id")
                hod = auth(client, "hod@lbauto.id")
                workshop = auth(client, "workshop@lbauto.id")
                sales = auth(client, "sales@lbauto.id")

                self.assertEqual(client.get("/api/dashboard", headers=owner).status_code, 200)
                self.assertEqual(client.post("/api/units", headers=sales, json={}).status_code, 403)

                cover_upload = client.post(
                    "/api/uploads?category=sourcing",
                    headers={**buyer, "Content-Type": "image/jpeg"},
                    content=b"demo-cover-image",
                )
                self.assertEqual(cover_upload.status_code, 201, cover_upload.text)
                cover_url = cover_upload.json()["url"]

                created = client.post("/api/units", headers=buyer, json={
                    "brand": "Porsche", "model": "Macan S", "year": 2023,
                    "color": "Carrara White", "plate": "B 9090 LBA", "transmission": "AT",
                    "km": 8900, "vin": "WP1ZZZ95ZPLB09090", "engine_number": "DGM09090",
                    "source": "Perorangan", "seller": "Demo Seller", "seller_phone": "081234567890",
                    "location": "Jakarta Selatan", "offer_price": 1550000000, "target_price": 1490000000,
                    "cover_photo": cover_url,
                })
                self.assertEqual(created.status_code, 201, created.text)
                unit_id = created.json()["id"]
                self.assertEqual(created.json()["status"], "SOURCED")
                self.assertEqual(created.json()["source_photos"][0], cover_url)

                initial = client.post(f"/api/units/{unit_id}/initial-qc", headers=leader, json={"approved": True, "notes": "Layak diperiksa"})
                self.assertEqual(initial.json()["status"], "INITIAL_QC")
                legal_check = client.post(f"/api/units/{unit_id}/legal-precheck", headers=legal, json={
                    "stnk_available": True, "bpkb_available": True, "vin_match": True,
                    "engine_match": True, "tax_checked": True, "notes": "Identitas sesuai",
                })
                self.assertEqual(legal_check.json()["status"], "LEGAL_PRECHECK")
                checkers = client.get("/api/users?role=ROLE_FIELD_CHECKER", headers=leader).json()
                assigned = client.post(f"/api/units/{unit_id}/assign", headers=leader, json={"checker_id": checkers[0]["id"]})
                self.assertEqual(assigned.json()["status"], "CHECKER_ASSIGNED")
                self.assertEqual(client.post(f"/api/units/{unit_id}/inspection", headers=buyer, json={}).status_code, 403)

                inspected = client.post(f"/api/units/{unit_id}/inspection", headers=checker, json={
                    "body_score": 94, "major_accident": False, "flood": False,
                    "engine_condition": "Halus/Normal", "oil_condition": "Kering",
                    "suspension_condition": "Senyap/Normal", "tax_status": "Pajak Hidup",
                    "notes": "Unit sangat terawat", "photos": [f"/uploads/inspection/{i}.jpg" for i in range(8)],
                })
                self.assertEqual(inspected.status_code, 200, inspected.text)
                self.assertEqual(inspected.json()["status"], "REPORT_SUBMITTED")

                self.assertEqual(client.post(f"/api/units/{unit_id}/purchase-decision", headers=buyer, json={"decision":"DEAL","final_price":1490000000}).status_code, 403)
                decision = client.post(f"/api/units/{unit_id}/purchase-decision", headers=hod, json={
                    "decision": "DEAL", "final_price": 1490000000, "payment_method": "Transfer Bank",
                })
                self.assertEqual(decision.json()["status"], "HOD_APPROVED")
                voucher = client.post(f"/api/units/{unit_id}/payment-request", headers=buyer, json={
                    "voucher_number": "PV-2026-0001", "amount": 1490000000, "method": "Transfer Bank",
                })
                self.assertEqual(voucher.json()["status"], "PAYMENT_PENDING")
                paid = client.post(f"/api/units/{unit_id}/payment-confirm", headers=buyer, json={"proof_url":"/uploads/payment/proof.jpg"})
                self.assertEqual(paid.json()["status"], "PURCHASED_PAID")
                handover = client.post(f"/api/units/{unit_id}/repair-handover", headers=workshop, json={"odometer": 8905, "notes":"Diterima utuh"})
                self.assertEqual(handover.json()["status"], "REPAIR_HANDOVER")

                repaired = client.put(f"/api/units/{unit_id}/repair", headers=workshop, json={
                    "categories": ["Bumper Repair"], "vendor": "Workshop LB AUTO",
                    "stage": "CLEAR_COAT", "estimated_cost": 5000000, "actual_cost": 4500000,
                    "progress": 100, "target_date": "2026-08-20", "notes": "Final QC selesai",
                    "work_items": [{"category":"Bumper Repair","panel":"Bumper depan","progress":100,"estimated_cost":5000000,"actual_cost":4500000}],
                    "before_photos": ["/uploads/repair_before/before.jpg"], "after_photos": ["/uploads/repair_after/after.jpg"],
                })
                self.assertEqual(repaired.json()["status"], "REPAIR_QC")
                qc = client.post(f"/api/units/{unit_id}/repair-qc", headers=hod, json={"approved":True,"notes":"Hasil rapi"})
                self.assertEqual(qc.json()["status"], "DOCUMENT_QC")
                documents = client.put(f"/api/units/{unit_id}/documents", headers=legal, json={
                    "stnk_status": "ADA_ASLI", "tax_due": "2027-08-01", "plate_due": "2031-08-01",
                    "bpkb_status": "ADA_ASLI", "bpkb_number": "BPKB-9090",
                    "invoice_status": "LENGKAP", "receipt_available": True, "owner_id_copy": True,
                    "items": ["Kunci Cadangan", "Buku Servis"],
                })
                self.assertEqual(documents.json()["documents"]["ready_for_sale"], 1)
                self.assertEqual(documents.json()["status"], "READY_TO_SELL")

                listing = client.put(f"/api/units/{unit_id}/listing", headers=sales, json={
                    "media_items": ["https://example.com/macans.jpg"], "video_url": None,
                    "cash_price": 1650000000, "credit_price": 1675000000,
                    "description": "Porsche Macan S siap jual", "channels": ["OLX", "Instagram"],
                    "publish": True,
                })
                self.assertEqual(listing.status_code, 200, listing.text)
                self.assertEqual(listing.json()["status"], "PUBLISHED")
                simulation = client.post("/api/credit-simulation", headers=sales, json={
                    "otr_price": 1650000000, "total_down_payment": 500000000,
                    "tenor_months": 36, "annual_interest_rate": 8.5,
                    "admin_fee": 5000000, "insurance_fee": 20000000,
                })
                self.assertEqual(simulation.status_code, 200)
                self.assertGreater(simulation.json()["monthly_installment"], 0)

                lead = client.post("/api/leads", headers=sales, json={
                    "name": "Prospect Demo", "phone": "081288880000", "unit_id": unit_id,
                    "source": "Instagram", "notes": "Menanyakan jadwal test drive",
                })
                self.assertEqual(lead.status_code, 201, lead.text)
                lead_id = lead.json()["id"]
                direct_move = client.patch(f"/api/leads/{lead_id}/status", headers=sales, json={
                    "status": "TEST_DRIVE", "notes": "Langsung memilih jadwal test drive",
                })
                self.assertEqual(direct_move.json()["status"], "TEST_DRIVE")
                cancelled = client.patch(f"/api/leads/{lead_id}/status", headers=sales, json={
                    "status": "CANCELLED", "notes": "Customer membatalkan minat",
                })
                self.assertEqual(cancelled.json()["status"], "CANCELLED")
                reopened = client.patch(f"/api/leads/{lead_id}/status", headers=sales, json={
                    "status": "FOLLOW_UP", "notes": "Customer ingin dihubungi kembali",
                })
                self.assertEqual(reopened.json()["status"], "FOLLOW_UP")

                sold = client.post("/api/sales", headers=sales, json={
                    "unit_id": unit_id, "buyer_name": "Customer Demo", "buyer_phone": "081200001111",
                    "buyer_nik": "3174000000000001", "buyer_address": "Jakarta",
                    "payment_scheme": "CASH", "down_payment": 0, "final_price": 1650000000,
                    "delivered_at": "2026-08-25",
                })
                self.assertEqual(sold.status_code, 201, sold.text)
                self.assertEqual(sold.json()["status"], "BOOKED")
                paid_sale = client.post(f"/api/sales/{unit_id}/payment-process", headers=sales)
                self.assertEqual(paid_sale.json()["status"], "CASH_CONFIRMED")
                deal = client.post(f"/api/sales/{unit_id}/deal", headers=sales)
                self.assertEqual(deal.json()["status"], "DEAL")
                scheduled = client.post(f"/api/sales/{unit_id}/schedule-delivery", headers=sales, json={"scheduled_at":"2026-08-25T10:00:00+07:00"})
                self.assertEqual(scheduled.json()["status"], "DELIVERY_SCHEDULED")
                completed = client.post(f"/api/sales/{unit_id}/complete-delivery", headers=sales, json={"notes":"Unit diterima"})
                self.assertEqual(completed.json()["status"], "SOLD_DELIVERED")
                self.assertEqual(completed.json()["profit"], 155500000)
                greeting = client.post(f"/api/units/{unit_id}/greeting", headers=sales, json={
                    "media_url": "/uploads/greeting/delivery.jpg", "rating": 5,
                    "consent": True, "notes": "Customer puas",
                })
                self.assertEqual(greeting.status_code, 200, greeting.text)
                self.assertEqual(greeting.json()["greeting"]["rating"], 5)
                self.assertEqual(client.get(f"/api/sales/{unit_id}/document/spk", headers=sales).status_code, 200)

                report = client.get("/api/reports/financial", headers=owner)
                self.assertTrue(any(unit["id"] == unit_id for unit in report.json()["units"]))
                pdf_export = client.get("/api/reports/export/pdf", headers=owner)
                self.assertEqual(pdf_export.status_code, 200, pdf_export.text)
                self.assertEqual(pdf_export.headers["content-type"], "application/pdf")
                self.assertTrue(pdf_export.content.startswith(b"%PDF"))
                excel_export = client.get("/api/reports/export/excel", headers=owner)
                self.assertEqual(excel_export.status_code, 200, excel_export.text)
                self.assertIn("spreadsheetml", excel_export.headers["content-type"])
                self.assertTrue(excel_export.content.startswith(b"PK"))

                credit_booking = client.post("/api/sales", headers=sales, json={
                    "unit_id": "LBA-2026-0088", "buyer_name": "Credit Customer", "buyer_phone": "081299990000",
                    "payment_scheme": "CREDIT", "leasing_vendor": "BCA Finance", "tenor_months": 36,
                    "down_payment": 250000000, "final_price": 795000000,
                })
                self.assertEqual(credit_booking.status_code, 201, credit_booking.text)
                finance = client.post("/api/sales/LBA-2026-0088/payment-process", headers=sales)
                self.assertEqual(finance.json()["status"], "SURVEY_FINANCE")
                survey = client.post("/api/sales/LBA-2026-0088/survey-complete", headers=sales)
                self.assertEqual(survey.json()["status"], "FINANCE_PROCESS")
                approved = client.post("/api/sales/LBA-2026-0088/finance-approval", headers=sales, json={
                    "approved": True, "reference": "BCAF-2026-001", "notes": "Survey disetujui",
                })
                self.assertEqual(approved.json()["status"], "FINANCE_APPROVED")
                self.assertEqual(approved.json()["sale"]["leasing_vendor"], "BCA Finance")
                logs = client.get("/api/audit-logs", headers=owner)
                self.assertGreaterEqual(len(logs.json()), 10)


if __name__ == "__main__":
    unittest.main()
