# LB AUTO Operations

PWA mobile-first untuk mengelola alur sourcing, inspeksi, pembelian, repair, dokumen, CRM, penjualan, dan laporan showroom LB AUTO. Frontend menggunakan HTML/CSS/JavaScript tanpa build step. Backend menggunakan FastAPI dan SQLite.

## Dokumentasi

- [Panduan penggunaan lengkap](PANDUAN%20PENGGUNAAN%20LENGKAP.md)
- [Flow video demo client](FLOW%20VIDEO%20DEMO%20CLIENT.md)
- [Deployment systemd dan Cloudflare Tunnel](PANDUAN%20DEPLOYMENT%20SYSTEMD%20DAN%20CLOUDFLARE%20TUNNEL.md)

## Menjalankan aplikasi

```bash
python3 -m backend.seed
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8542 --reload
```

Buka `http://127.0.0.1:8542`. Dokumentasi API tersedia di `http://127.0.0.1:8542/docs`.

## Akun demo

Semua akun menggunakan password `LBAuto123!`.

| Role | Email |
| --- | --- |
| Owner | owner@lbauto.id |
| PIC Pembelian | krisna@lbauto.id |
| Inspection Leader | ciprut@lbauto.id |
| Field Checker | checker@lbauto.id |
| PIC Legal | legal@lbauto.id |
| Head of Department | hod@lbauto.id |
| PIC Workshop | workshop@lbauto.id |
| Sales & Marketing | sales@lbauto.id |

## Pengujian

```bash
python3 -m unittest -v
```

Integration test menjalankan alur lengkap mulai dari input unit sampai penjualan dan memverifikasi pembatasan RBAC.

## Notifikasi WhatsApp

Konfigurasi Fonnte dibaca dari `.env` dan tidak pernah dikirim ke frontend. Isi nomor WhatsApp setiap approver melalui menu **User management → Atur WA**. Jika nomor belum diatur, event tetap tersimpan di log notifikasi dengan status `SKIPPED_NO_TARGET`.

```env
FONNTE_ENABLED=true
FONNTE_TOKEN=token-fonnte-anda
APP_BASE_URL=http://127.0.0.1:8542
```

Flow unit yang dipaksakan server: Initial QC → legal precheck → inspeksi 8 foto → approval HOD → voucher dan bukti bayar → serah-terima repair → pekerjaan per panel → Repair QC → Document QC → listing → booking → pembayaran/finance → deal → jadwal delivery → delivery selesai.

## Konfigurasi produksi

Set `LB_AUTO_SECRET` ke nilai acak yang kuat sebelum deployment. Gunakan reverse proxy HTTPS, batasi akses file database, ganti password demo, dan jalankan satu worker selama masih menggunakan SQLite.
