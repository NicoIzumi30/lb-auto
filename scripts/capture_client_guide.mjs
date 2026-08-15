import playwright from "/tmp/lb-auto-playwright/node_modules/playwright/index.js";
import fs from "node:fs";
import path from "node:path";

const BASE = "http://127.0.0.1:8010";
const ROOT = "/home/yuki-x2/project/LB-AUTO";
const OUT = path.join(ROOT, "assets", "panduan-client");
const PASSWORD = "LBAuto123!";
const demoSuffix = String(Date.now()).slice(-4);
const assets = {
  cover: path.join(ROOT, "demo-assets", "00-cover-unit.png"),
  inspection: [
    "01-depan.jpg", "02-belakang.jpg", "03-kanan.jpg", "04-kiri.jpg",
    "05-mesin.jpg", "06-interior.jpg", "07-rangka.jpg", "08-odometer.jpg",
  ].map((name) => path.join(ROOT, "demo-assets", name)),
  payment: path.join(ROOT, "demo-assets", "08-odometer.jpg"),
  before: path.join(ROOT, "assets", "demo-repair", "repair-before.png"),
  after: path.join(ROOT, "assets", "demo-repair", "repair-after.png"),
  greeting: path.join(ROOT, "demo-assets", "00-cover-unit.png"),
};

fs.mkdirSync(OUT, { recursive: true });
for (const name of fs.readdirSync(OUT)) {
  if (name.endsWith(".png")) fs.unlinkSync(path.join(OUT, name));
}

const { chromium } = playwright;
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 430, height: 932 },
  deviceScaleFactor: 1,
  locale: "id-ID",
  timezoneId: "Asia/Jakarta",
  serviceWorkers: "block",
});
const page = await context.newPage();
page.setDefaultTimeout(20000);

async function settle(ms = 550) {
  await page.waitForTimeout(ms);
  await page.locator(".loading").waitFor({ state: "detached", timeout: 10000 }).catch(() => {});
}

async function capture(name) {
  await settle(250);
  await page.screenshot({ path: path.join(OUT, `${name}.png`), fullPage: false });
  console.log(`captured ${name}`);
}

async function captureModal(name) {
  await page.locator("#modal").waitFor({ state: "visible" });
  await page.locator(".modal").evaluate((element) => { element.scrollTop = 0; });
  await capture(name);
}

async function captureTarget(selector, name) {
  const target = page.locator(selector).first();
  await target.waitFor({ state: "visible" });
  await target.scrollIntoViewIfNeeded();
  await target.evaluate((element) => element.setAttribute("data-guide-target", "true"));
  const style = await page.addStyleTag({ content: `
    [data-guide-target="true"] { position:relative!important; z-index:9998!important; outline:4px solid #ffd84d!important; outline-offset:4px!important; box-shadow:0 0 0 8px rgba(23,26,25,.34)!important; }
    #guide-callout { position:fixed; z-index:9999; padding:6px 10px; border:2px solid #ffd84d; border-radius:8px; background:#171a19; color:white; font-size:9px; font-weight:900; letter-spacing:.07em; white-space:nowrap; box-shadow:0 5px 14px rgba(0,0,0,.28); pointer-events:none; }
  ` });
  await target.evaluate((element) => {
    const rect = element.getBoundingClientRect();
    const callout = document.createElement("div");
    callout.id = "guide-callout";
    callout.textContent = "TEKAN DI SINI";
    const below = rect.bottom + 48 < window.innerHeight;
    callout.style.top = `${below ? rect.bottom + 12 : Math.max(8, rect.top - 38)}px`;
    callout.style.left = `${Math.min(window.innerWidth - 118, Math.max(8, rect.left + rect.width / 2 - 55))}px`;
    document.body.append(callout);
  });
  await capture(name);
  await target.evaluate((element) => element.removeAttribute("data-guide-target"));
  await page.locator("#guide-callout").evaluate((element) => element.remove());
  await style.evaluate((element) => element.remove());
}

async function login(email, screenshotName = null) {
  await page.goto(BASE, { waitUntil: "domcontentloaded" });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.locator("#login-form").waitFor();
  await page.locator('[name="email"]').fill(email);
  await page.locator('[name="password"]').fill(PASSWORD);
  if (screenshotName) await capture(screenshotName);
  await page.locator('#login-form button[type="submit"]').click();
  await page.locator(".app-shell").waitFor();
  await settle();
  console.log(`login ${email}`);
}

async function go(route) {
  await page.goto(`${BASE}/#${route}`, { waitUntil: "domcontentloaded" });
  await page.locator(".app-shell").waitFor();
  await settle();
}

async function openUnit(route, unitId) {
  await go(route);
  const target = page.locator(`[data-unit="${unitId}"]`).first();
  await target.waitFor({ state: "visible" });
  await target.click();
  await page.locator(".detail-hero").waitFor();
  await settle();
}

async function openAction(action, beforeName) {
  const button = page.locator(`[data-action="${action}"]`).first();
  await button.waitFor({ state: "visible" });
  if (beforeName) await captureTarget(`[data-action="${action}"]`, beforeName);
  await button.click();
  await page.locator("#modal").waitFor({ state: "visible" });
}

async function submitModal(formSelector) {
  const form = page.locator(formSelector);
  await form.locator('button[type="submit"], button:not([type])').last().click();
  try {
    await page.locator("#modal").waitFor({ state: "detached", timeout: 30000 });
  } catch (error) {
    const message = await page.locator(".toast.error").last().textContent().catch(() => "unknown modal error");
    throw new Error(`${formSelector}: ${message}`);
  }
  await settle(700);
}

async function fill(name, value, scope = page) {
  await scope.locator(`[name="${name}"]`).fill(String(value));
}

async function choose(name, value, scope = page) {
  await scope.locator(`[name="${name}"]`).selectOption(String(value));
}

let unitId = "";
try {
  await login("krisna@lbauto.id", "01-login-pic-pembelian");
  await capture("02-home-pic-pembelian");
  await captureTarget('.bottom-nav [data-route="acquisition"]', "02a-pilih-menu-sourcing");
  await go("acquisition");
  const unitForm = page.locator("#unit-form");
  await choose("source", "Perorangan", unitForm);
  await fill("seller", "Budi Santoso", unitForm);
  await fill("seller_phone", "081298765432", unitForm);
  await fill("location", "Jakarta Selatan", unitForm);
  await choose("brand", "Lexus", unitForm);
  await fill("model", "RX 300 Luxury", unitForm);
  await fill("year", "2022", unitForm);
  await choose("transmission", "AT", unitForm);
  await fill("color", "Sonic Quartz", unitForm);
  await fill("plate", `B ${demoSuffix} LBA`, unitForm);
  await fill("vin", `JTJZZZRX300LBA${demoSuffix}`, unitForm);
  await fill("engine_number", `LBA8AR${demoSuffix}`, unitForm);
  await fill("km", "18500", unitForm);
  await fill("offer_price", "795000000", unitForm);
  await fill("target_price", "775000000", unitForm);
  await unitForm.locator('[name="cover_photo"]').setInputFiles(assets.cover);
  await capture("03-form-sourcing-terisi");
  await unitForm.locator('button[type="submit"]').click();
  await page.waitForURL(/#unit\//, { timeout: 30000 });
  await page.locator(".detail-hero").waitFor();
  unitId = page.url().split("#unit/")[1];
  fs.writeFileSync(path.join(OUT, "unit-id.txt"), `${unitId}\n`);
  await capture("04-unit-berhasil-dicatat");

  await login("ciprut@lbauto.id");
  await openUnit("inspection", unitId);
  await openAction("initial-qc", "05a-pilih-tombol-initial-qc");
  await choose("approved", "true", page.locator("#initial-qc-form"));
  await fill("notes", "Kondisi awal layak diteruskan ke pemeriksaan legal.", page.locator("#initial-qc-form"));
  await captureModal("05-initial-qc-inspection-leader");
  await submitModal("#initial-qc-form");

  await login("legal@lbauto.id");
  await openUnit("inspection", unitId);
  await openAction("legal-precheck", "06a-pilih-tombol-pemeriksaan-legal");
  const legalForm = page.locator("#legal-form");
  for (const name of ["stnk_available", "bpkb_available", "vin_match", "engine_match", "tax_checked"]) {
    await legalForm.locator(`[name="${name}"]`).check();
  }
  await fill("notes", "Identitas kendaraan dan dokumen sesuai.", legalForm);
  await captureModal("06-pemeriksaan-legal-awal");
  await submitModal("#legal-form");

  await login("ciprut@lbauto.id");
  await openUnit("inspection", unitId);
  await openAction("assign", "07a-pilih-tombol-tugaskan-checker");
  const assignForm = page.locator("#assign-form");
  await assignForm.locator('[name="checker_id"]').selectOption({ index: 1 });
  await captureModal("07-penugasan-field-checker");
  await submitModal("#assign-form");

  await login("checker@lbauto.id");
  await openUnit("inspection", unitId);
  await openAction("inspection", "08a-pilih-tombol-isi-inspeksi");
  const inspectionForm = page.locator("#inspection-form");
  await fill("body_score", "91", inspectionForm);
  await choose("engine_condition", "Halus/Normal", inspectionForm);
  await choose("oil_condition", "Kering", inspectionForm);
  await choose("suspension_condition", "Senyap/Normal", inspectionForm);
  await choose("major_accident", "false", inspectionForm);
  await choose("flood", "false", inspectionForm);
  await choose("tax_status", "Pajak Hidup", inspectionForm);
  await fill("notes", "Baret dan penyok ringan pada bumper serta fender depan kiri.", inspectionForm);
  for (let index = 0; index < assets.inspection.length; index += 1) {
    await inspectionForm.locator(`[name="photo_${index}"]`).setInputFiles(assets.inspection[index]);
  }
  await captureModal("08-form-inspeksi-dan-delapan-foto");
  await inspectionForm.locator(".upload-field").first().scrollIntoViewIfNeeded();
  await capture("08b-area-upload-delapan-foto");
  await submitModal("#inspection-form");
  await page.locator('[data-tab="inspection"]').click();
  await settle();
  await capture("09-hasil-inspeksi-delapan-foto");

  await login("hod@lbauto.id");
  await openUnit("inspection", unitId);
  await openAction("decision", "10a-pilih-tombol-keputusan-hod");
  const decisionForm = page.locator("#decision-form");
  await choose("decision", "DEAL", decisionForm);
  await fill("final_price", "780000000", decisionForm);
  await fill("rejection_reason", "Disetujui sesuai hasil inspeksi dan harga final.", decisionForm);
  await captureModal("10-keputusan-pembelian-hod");
  await submitModal("#decision-form");

  await login("krisna@lbauto.id");
  await openUnit("inventory", unitId);
  await openAction("payment-request", "11a-pilih-tombol-buat-voucher");
  const voucherForm = page.locator("#payment-request-form");
  await fill("voucher_number", `PV-${unitId.replaceAll("LBA-", "")}`, voucherForm);
  await fill("amount", "780000000", voucherForm);
  await choose("method", "Transfer Bank", voucherForm);
  await captureModal("11-voucher-pembayaran");
  await submitModal("#payment-request-form");
  await openAction("payment-confirm", "12a-pilih-tombol-konfirmasi-pembayaran");
  const paymentForm = page.locator("#payment-confirm-form");
  await paymentForm.locator('[name="proof"]').setInputFiles(assets.payment);
  await fill("paid_at", "2026-08-24T10:30", paymentForm);
  await captureModal("12-konfirmasi-dan-bukti-pembayaran");
  await submitModal("#payment-confirm-form");

  await login("workshop@lbauto.id");
  await openUnit("workshop", unitId);
  await openAction("repair-handover", "13a-pilih-tombol-terima-unit");
  const handoverForm = page.locator("#handover-form");
  await fill("odometer", "18512", handoverForm);
  await fill("notes", "Unit diterima lengkap, kerusakan sesuai laporan inspeksi.", handoverForm);
  await captureModal("13-serah-terima-workshop");
  await submitModal("#handover-form");
  await openAction("repair", "14a-pilih-tombol-update-repair");
  const repairForm = page.locator("#repair-form");
  await fill("vendor", "Workshop Body Repair LB AUTO", repairForm);
  await choose("stage", "CLEAR_COAT", repairForm);
  await fill("target_date", "2026-08-27", repairForm);
  await choose("category_0", "Bumper Repair", repairForm);
  await fill("panel_0", "Bumper dan fender depan kiri", repairForm);
  await fill("progress_0", "100", repairForm);
  await fill("estimated_0", "8500000", repairForm);
  await fill("actual_0", "8000000", repairForm);
  await repairForm.locator('[name="before_photos"]').setInputFiles(assets.before);
  await repairForm.locator('[name="after_photos"]').setInputFiles(assets.after);
  await fill("notes", "Body repair, pengecatan, clear coat, dan polishing selesai.", repairForm);
  await captureModal("14-update-repair-before-after");
  await repairForm.locator('[name="before_photos"]').scrollIntoViewIfNeeded();
  await capture("14b-area-upload-before-after");
  await submitModal("#repair-form");
  await page.locator('[data-tab="repair"]').click();
  await settle();
  await capture("15-galeri-before-after-repair");

  await login("hod@lbauto.id");
  await openUnit("workshop", unitId);
  await openAction("repair-qc", "16a-pilih-tombol-approval-repair-qc");
  const qcForm = page.locator("#repair-qc-form");
  await choose("approved", "true", qcForm);
  await fill("notes", "Hasil repair rapi, warna sesuai, dan panel presisi.", qcForm);
  await captureModal("16-approval-repair-qc");
  await submitModal("#repair-qc-form");

  await login("legal@lbauto.id");
  await openUnit("workshop", unitId);
  await openAction("documents", "17a-pilih-tombol-document-qc");
  const documentsForm = page.locator("#documents-form");
  await choose("stnk_status", "ADA_ASLI", documentsForm);
  await fill("tax_due", "2027-08-24", documentsForm);
  await choose("bpkb_status", "ADA_ASLI", documentsForm);
  await fill("bpkb_number", "BPKB-LBA-2408", documentsForm);
  await choose("invoice_status", "LENGKAP", documentsForm);
  await documentsForm.locator('[name="receipt_available"]').check();
  await documentsForm.locator('[name="owner_id_copy"]').check();
  await captureModal("17-document-qc-pic-legal");
  await submitModal("#documents-form");

  await login("sales@lbauto.id");
  await openUnit("inventory", unitId);
  await openAction("listing", "18a-pilih-tombol-media-listing");
  const listingForm = page.locator("#listing-form");
  await fill("cash_price", "865000000", listingForm);
  await fill("credit_price", "885000000", listingForm);
  await fill("video_url", "https://example.com/video-rx300", listingForm);
  await fill("media_items", "https://example.com/media/rx300-1.jpg, https://example.com/media/rx300-2.jpg", listingForm);
  await fill("description", "Lexus RX 300 Luxury 2022, dokumen lengkap, kondisi terawat, dan siap digunakan.", listingForm);
  await listingForm.locator('[name="channels"][value="OLX"]').check();
  await listingForm.locator('[name="channels"][value="Instagram"]').check();
  await listingForm.locator('[name="channels"][value="Facebook Marketplace"]').check();
  await listingForm.locator('[name="publish"]').check();
  await captureModal("18-media-dan-listing");
  await submitModal("#listing-form");
  await openAction("sale", "19a-pilih-tombol-booking-customer");
  const saleForm = page.locator("#sale-form");
  await fill("buyer_name", "Andi Wijaya", saleForm);
  await fill("buyer_phone", "081211112222", saleForm);
  await choose("payment_scheme", "CASH", saleForm);
  await fill("final_price", "855000000", saleForm);
  await fill("buyer_nik", "3174012408900001", saleForm);
  await fill("buyer_address", "Kebayoran Baru, Jakarta Selatan", saleForm);
  await fill("down_payment", "0", saleForm);
  await captureModal("19-booking-customer");
  await submitModal("#sale-form");
  await openAction("payment-process", "20a-pilih-tombol-mulai-pembayaran");
  await captureModal("20-konfirmasi-pembayaran-cash");
  await submitModal("#payment-process-form");
  await openAction("deal", "21a-pilih-tombol-tandai-deal");
  await captureModal("21-konfirmasi-deal");
  await submitModal("#deal-form");
  await openAction("schedule-delivery", "22a-pilih-tombol-jadwalkan-delivery");
  const scheduleForm = page.locator("#schedule-form");
  await fill("scheduled_at", "2026-08-30T10:00", scheduleForm);
  await fill("notes", "Delivery di showroom LB AUTO, unit sudah dipoles dan diisi bahan bakar.", scheduleForm);
  await captureModal("22-jadwal-delivery");
  await submitModal("#schedule-form");
  await openAction("complete-delivery", "23a-pilih-tombol-selesaikan-delivery");
  const deliveryForm = page.locator("#complete-delivery-form");
  await fill("notes", "Unit, kunci, dan dokumen diterima customer dalam kondisi baik.", deliveryForm);
  await captureModal("23-penyelesaian-delivery");
  await submitModal("#complete-delivery-form");
  await openAction("greeting", "24a-pilih-tombol-greeting");
  const greetingForm = page.locator("#greeting-form");
  await greetingForm.locator('[name="greeting_media"]').setInputFiles(assets.greeting);
  await choose("rating", "5", greetingForm);
  await fill("notes", "Customer puas dengan pelayanan dan kondisi kendaraan.", greetingForm);
  await greetingForm.locator('[name="consent"]').check();
  await captureModal("24-delivery-greeting-dan-consent");
  await submitModal("#greeting-form");
  await capture("25-unit-selesai-diserahkan");

  await go("sales");
  await captureTarget('[data-action="add-lead"]', "26a-pilih-tombol-tambah-lead");
  await page.locator('[data-action="add-lead"]').click();
  const leadForm = page.locator("#lead-form");
  await fill("name", "Rina Kusuma", leadForm);
  await fill("phone", "081233344455", leadForm);
  await choose("source", "Instagram", leadForm);
  await choose("unit_id", unitId, leadForm);
  await fill("notes", "Customer meminta informasi stok kendaraan premium.", leadForm);
  await captureModal("26-input-customer-lead");
  await submitModal("#lead-form");
  await capture("27-daftar-customer-leads");
  const leadCard = page.locator(".crm-card").filter({ hasText: "Rina Kusuma" }).first();
  await captureTarget(".crm-card:has-text('Rina Kusuma') [data-lead]", "28a-pilih-tombol-ubah-status-lead");
  await leadCard.locator("[data-lead]").click();
  const leadStatusForm = page.locator("#lead-status-form");
  await choose("status", "CANCELLED", leadStatusForm);
  await fill("notes", "Customer menunda pembelian.", leadStatusForm);
  await captureModal("28-pilih-status-customer-lead");
  await submitModal("#lead-status-form");

  await login("owner@lbauto.id");
  await go("dashboard");
  await capture("30-home-owner");
  await go("reports");
  await capture("29-laporan-dan-export-owner");

  console.log(`DONE unit=${unitId}`);
} finally {
  await context.close();
  await browser.close();
}
