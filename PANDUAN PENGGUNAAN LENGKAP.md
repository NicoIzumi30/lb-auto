# Panduan Penggunaan Lengkap LB AUTO

Panduan ini menjelaskan penggunaan aplikasi LB AUTO dari konfigurasi awal, input unit, inspeksi, pembelian, repair, penjualan, hingga unit selesai diserahkan kepada customer.

Terakhir diperbarui: 15 Agustus 2026, untuk PWA versi 22.

## 1. Membuka aplikasi

Jalankan aplikasi dari direktori proyek:

```bash
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Kemudian buka:

- Aplikasi: `http://127.0.0.1:8000`
- Dokumentasi API: `http://127.0.0.1:8000/docs`
- Pemeriksaan server: `http://127.0.0.1:8000/api/health`

Semua akun demo menggunakan password:

```text
LBAuto123!
```

### Navigasi aplikasi

Pada mobile, navigasi bawah dibuat rata tanpa tombol yang menonjol dan berisi:

- **Home**: ringkasan operasional dan seluruh menu tambahan.
- **Stok**: daftar serta pencarian unit.
- **Inspeksi**: antrean dan proses pemeriksaan kendaraan.
- **Sales & CRM**: lead serta aktivitas penjualan.

Menu **Sourcing** tidak berada di navigasi bawah. Untuk membukanya, masuk ke **Home**, lalu pilih **Sourcing unit** pada bagian **Menu**. Kalender, Workshop, Simulator Kredit, Laporan, User & RBAC, dan Audit Trail juga tersedia melalui menu di Home sesuai hak akses akun.

Pada desktop, menu operasional tetap tersedia melalui sidebar. Untuk keluar dari aplikasi, tekan profil di pojok kanan atas lalu pilih **Logout**. Pada desktop, tombol logout juga tersedia di kartu profil sidebar.

## 2. Daftar akun dan tanggung jawab

| Urutan | Role | Email | Tanggung jawab utama |
| --- | --- | --- | --- |
| 1 | Owner | `owner@lbauto.id` | Mengelola user, nomor WhatsApp, laporan, dan audit |
| 2 | PIC Pembelian | `krisna@lbauto.id` | Input unit, voucher, dan konfirmasi pembayaran |
| 3 | Inspection Leader | `ciprut@lbauto.id` | Initial QC dan penugasan checker |
| 4 | PIC Legal | `legal@lbauto.id` | Pemeriksaan legal awal dan Document QC |
| 5 | Field Checker | `checker@lbauto.id` | Inspeksi fisik dan unggah delapan foto |
| 6 | Head of Department | `hod@lbauto.id` | Keputusan pembelian dan Repair QC |
| 7 | PIC Workshop | `workshop@lbauto.id` | Serah-terima serta pekerjaan repair |
| 8 | Sales & Marketing | `sales@lbauto.id` | Listing, booking, finance, delivery, dan greeting |

Owner memiliki akses penuh sebagai cadangan, tetapi proses operasional sebaiknya tetap dijalankan menggunakan akun role masing-masing agar audit trail jelas.

## 3. Konfigurasi awal oleh Owner

Login terlebih dahulu menggunakan:

```text
Email: owner@lbauto.id
Password: LBAuto123!
```

Setelah masuk:

1. Buka **Home**.
2. Pilih menu **User & RBAC** atau buka **User management** dari sidebar desktop.
3. Cari setiap user yang menerima approval.
4. Tekan **Atur WA**.
5. Masukkan nomor WhatsApp dalam format `62`, misalnya `6281234567890`.
6. Tekan **Simpan nomor**.

Nomor yang paling penting untuk dikonfigurasi:

- Inspection Leader
- PIC Legal
- Head of Department
- PIC Pembelian
- PIC Workshop
- Sales & Marketing

Notifikasi WhatsApp dikirim ketika suatu proses membutuhkan tindakan role berikutnya. Apabila nomor belum diatur, proses aplikasi tetap berjalan dan notifikasi dicatat sebagai `SKIPPED_NO_TARGET`.

Owner dapat menekan ikon lonceng di bagian atas untuk melihat log notifikasi, antara lain:

- `SENT`: berhasil dikirim melalui Fonnte.
- `FAILED`: pengiriman dicoba tetapi gagal.
- `SKIPPED_NO_TARGET`: tidak ada nomor WhatsApp pada role tujuan.
- `SKIPPED_DISABLED`: integrasi Fonnte sedang dinonaktifkan.

## 4. Ringkasan flow unit

```text
SOURCED
→ INITIAL_QC
→ LEGAL_PRECHECK
→ CHECKER_ASSIGNED
→ REPORT_SUBMITTED
→ HOD_APPROVED atau REJECTED
→ PAYMENT_PENDING
→ PURCHASED_PAID
→ REPAIR_HANDOVER
→ IN_REPAIR
→ REPAIR_QC
→ DOCUMENT_QC
→ READY_TO_SELL
→ PUBLISHED
→ BOOKED
→ SURVEY_FINANCE atau CASH_CONFIRMED
→ FINANCE_PROCESS
→ FINANCE_APPROVED
→ DEAL
→ DELIVERY_SCHEDULED
→ SOLD_DELIVERED
```

Cabang `SURVEY_FINANCE → FINANCE_PROCESS → FINANCE_APPROVED` hanya digunakan untuk transaksi kredit. Transaksi cash bergerak dari `BOOKED → CASH_CONFIRMED → DEAL`.

## 5. Flow lengkap dari awal sampai selesai

### Tahap A — Input unit oleh PIC Pembelian

Login menggunakan:

```text
Email: krisna@lbauto.id
Password: LBAuto123!
```

Langkah penggunaan:

1. Buka **Home**, lalu pilih **Sourcing unit** pada bagian **Menu**.
2. Isi sumber unit dan data penjual.
3. Isi merek, model, tahun, transmisi, warna, nomor polisi, nomor rangka, nomor mesin, dan odometer.
4. Isi harga penawaran serta target harga.
5. Pada bagian **Foto cover unit**, tekan kartu **Pilih foto**.
6. Ambil atau pilih tepat satu foto utama kendaraan.
7. Tekan **Simpan unit**.

Foto cover merupakan foto tersendiri untuk kartu Stok, detail unit, dan CRM. Foto ini **bukan** bagian dari delapan foto inspeksi yang diunggah Field Checker pada tahap berikutnya.

Untuk demonstrasi Porsche Macan S, gunakan:

```text
demo-assets/00-cover-unit.png
```

Hasil:

- Unit mendapatkan ID otomatis seperti `LBA-2026-0090`.
- Status menjadi `SOURCED`.
- Inspection Leader menerima notifikasi Initial QC.

### Tahap B — Initial QC oleh Inspection Leader

Keluar dari akun PIC Pembelian, kemudian login menggunakan:

```text
Email: ciprut@lbauto.id
Password: LBAuto123!
```

Langkah penggunaan:

1. Buka menu **Inspeksi**.
2. Pilih unit berstatus **Sourced**.
3. Tekan **Initial QC**.
4. Pilih hasil **Lolos** atau **Tolak**.
5. Isi catatan pemeriksaan.
6. Tekan **Simpan hasil QC**.

Jika lolos:

- Status menjadi `INITIAL_QC`.
- PIC Legal menerima notifikasi pemeriksaan legal awal.

Jika ditolak:

- Status menjadi `REJECTED`.
- Proses unit berhenti.

### Tahap C — Pemeriksaan legal awal oleh PIC Legal

Login menggunakan:

```text
Email: legal@lbauto.id
Password: LBAuto123!
```

Langkah penggunaan:

1. Buka menu **Inspeksi**.
2. Pilih unit berstatus **Initial QC**.
3. Tekan **Pemeriksaan legal**.
4. Pastikan seluruh poin berikut dicentang:
   - STNK tersedia.
   - BPKB tersedia.
   - Nomor rangka sesuai.
   - Nomor mesin sesuai.
   - Pajak sudah diperiksa.
5. Tambahkan catatan jika diperlukan.
6. Tekan **Loloskan pemeriksaan legal**.

Semua pemeriksaan harus lolos. Sistem tidak mengizinkan unit diteruskan apabila salah satu pemeriksaan belum terpenuhi.

Hasil:

- Status menjadi `LEGAL_PRECHECK`.
- Inspection Leader menerima notifikasi untuk menugaskan checker.

### Tahap D — Penugasan Field Checker

Login kembali sebagai Inspection Leader:

```text
Email: ciprut@lbauto.id
Password: LBAuto123!
```

Langkah penggunaan:

1. Buka **Inspeksi**.
2. Pilih unit berstatus **Legal cleared**.
3. Tekan **Tugaskan checker**.
4. Pilih Field Checker.
5. Tekan **Simpan penugasan**.

Hasil:

- Status menjadi `CHECKER_ASSIGNED`.
- Unit hanya dapat diinspeksi oleh checker yang ditugaskan atau user dengan akses penuh.

### Tahap E — Inspeksi kendaraan oleh Field Checker

Login menggunakan:

```text
Email: checker@lbauto.id
Password: LBAuto123!
```

Langkah penggunaan:

1. Buka **Inspeksi**.
2. Pilih unit yang menjadi tugas Anda.
3. Tekan **Isi inspeksi**.
4. Isi skor body dari 1 sampai 100.
5. Isi kondisi mesin, oli, kaki-kaki, indikasi tabrak besar, banjir, dan status pajak.
6. Isi catatan checker.
7. Ambil atau unggah tepat delapan foto:
   - Depan.
   - Belakang.
   - Sisi kanan.
   - Sisi kiri.
   - Ruang mesin.
   - Interior.
   - Nomor rangka.
   - Odometer.
8. Tekan **Kirim laporan**.

Di perangkat mobile, tekan kartu **Pilih foto** pada setiap sisi. Browser akan menawarkan sumber foto dari galeri, kamera, atau aplikasi file sesuai perangkat. Sistem menampilkan nama file yang sudah dipilih dan tidak menggunakan tampilan input file bawaan browser. Format yang didukung adalah JPG, PNG, dan WebP dengan ukuran maksimal 8 MB per file.

Untuk demo, gunakan file `01-depan.jpg` sampai `08-odometer.jpg` dari folder `demo-assets` sesuai urutan pada form. Jangan memasukkan `00-cover-unit.png` ke salah satu dari delapan field inspeksi.

Hasil:

- Status menjadi `REPORT_SUBMITTED`.
- HOD menerima notifikasi bahwa keputusan pembelian diperlukan.

### Tahap F — Keputusan pembelian oleh HOD

Login menggunakan:

```text
Email: hod@lbauto.id
Password: LBAuto123!
```

Langkah penggunaan:

1. Buka **Inspeksi**.
2. Pilih unit berstatus **Review HOD**.
3. Periksa tab **Inspeksi** pada detail unit.
4. Tekan **Keputusan HOD**.
5. Pilih **Deal beli** atau **Tolak unit**.
6. Jika deal, masukkan harga pembelian final.
7. Jika ditolak, isi alasan penolakan.
8. Tekan **Konfirmasi keputusan**.

Jika disetujui:

- Status menjadi `HOD_APPROVED`.
- PIC Pembelian menerima notifikasi untuk membuat voucher pembayaran.

Jika ditolak:

- Status menjadi `REJECTED`.
- Proses unit berhenti.

### Tahap G — Voucher dan pembayaran oleh PIC Pembelian

Login kembali sebagai PIC Pembelian:

```text
Email: krisna@lbauto.id
Password: LBAuto123!
```

#### Membuat voucher

1. Buka **Inventory**.
2. Pilih unit berstatus **Disetujui HOD**.
3. Tekan **Buat voucher**.
4. Isi nomor voucher yang unik.
5. Pastikan nominal sama dengan harga yang disetujui HOD.
6. Pilih metode pembayaran.
7. Tekan **Ajukan pembayaran**.

Hasil: status menjadi `PAYMENT_PENDING`.

#### Mengonfirmasi pembayaran

1. Buka kembali unit berstatus **Menunggu pembayaran**.
2. Tekan **Konfirmasi pembayaran**.
3. Ambil atau unggah foto bukti pembayaran.
4. Isi waktu pembayaran apabila diperlukan.
5. Tekan **Konfirmasi dibayar**.

Hasil:

- Status menjadi `PURCHASED_PAID`.
- PIC Workshop menerima notifikasi untuk menerima fisik unit.

### Tahap H — Serah-terima unit kepada PIC Workshop

Login menggunakan:

```text
Email: workshop@lbauto.id
Password: LBAuto123!
```

Langkah penggunaan:

1. Buka **Workshop**.
2. Pilih unit berstatus **Sudah dibeli**.
3. Tekan **Terima unit**.
4. Isi odometer saat unit diterima.
5. Isi catatan kondisi fisik.
6. Tekan **Konfirmasi terima unit**.

Hasil: status menjadi `REPAIR_HANDOVER`.

### Tahap I — Pekerjaan repair per panel

Masih menggunakan akun PIC Workshop:

1. Buka unit berstatus **Serah-terima repair** atau **Dalam repair**.
2. Tekan **Update repair**.
3. Isi vendor atau workshop.
4. Pilih tahap pekerjaan.
5. Isi target selesai.
6. Isi pekerjaan per panel, meliputi:
   - Kategori pekerjaan.
   - Nama panel atau bagian.
   - Progres pekerjaan.
   - Estimasi biaya.
   - Realisasi biaya.
7. Ambil atau unggah foto before.
8. Ambil atau unggah foto after ketika pekerjaan selesai.
9. Isi catatan.
10. Tekan **Simpan progres**.

Progres unit dihitung dari rata-rata seluruh item pekerjaan. Total estimasi dan realisasi biaya juga dihitung dari semua item.

Jika progres belum 100%:

- Status menjadi `IN_REPAIR`.
- PIC Workshop dapat memperbarui pekerjaan kembali.

Jika seluruh pekerjaan 100%:

- Foto before dan after wajib tersedia.
- Status menjadi `REPAIR_QC`.
- HOD menerima notifikasi approval Repair QC.

### Tahap J — Approval Repair QC oleh HOD

Login sebagai HOD:

```text
Email: hod@lbauto.id
Password: LBAuto123!
```

Langkah penggunaan:

1. Buka **Workshop**.
2. Pilih unit berstatus **Repair QC**.
3. Periksa pekerjaan dan foto before/after pada detail unit.
4. Tekan **Approval Repair QC**.
5. Pilih **Lulus QC** atau **Kembalikan ke workshop**.
6. Isi catatan HOD.
7. Simpan keputusan.

Jika lulus:

- Status menjadi `DOCUMENT_QC`.
- PIC Legal menerima notifikasi Document QC.

Jika dikembalikan:

- Status kembali menjadi `IN_REPAIR`.
- PIC Workshop harus memperbaiki dan mengajukan QC kembali.

### Tahap K — Document QC oleh PIC Legal

Login sebagai PIC Legal:

```text
Email: legal@lbauto.id
Password: LBAuto123!
```

Langkah penggunaan:

1. Buka **Workshop**.
2. Pilih unit berstatus **Document QC**.
3. Tekan **Document QC**.
4. Isi status STNK dan tanggal pajak.
5. Isi status serta nomor BPKB.
6. Isi status faktur dan NIK.
7. Centang ketersediaan kwitansi bermaterai.
8. Centang ketersediaan fotokopi KTP pemilik.
9. Tekan **Simpan dokumen**.

Unit hanya menjadi siap jual apabila seluruh syarat berikut terpenuhi:

- STNK berstatus `ADA_ASLI`.
- BPKB berstatus `ADA_ASLI`.
- Faktur berstatus `LENGKAP`.
- Kwitansi bermaterai tersedia.
- Fotokopi KTP pemilik tersedia.

Jika lengkap, status menjadi `READY_TO_SELL`. Jika belum lengkap, status tetap `DOCUMENT_QC` dan listing belum dapat dibuat.

### Tahap L — Listing oleh Sales & Marketing

Login menggunakan:

```text
Email: sales@lbauto.id
Password: LBAuto123!
```

Langkah penggunaan:

1. Buka **Inventory**.
2. Pilih unit berstatus **Siap jual**.
3. Tekan **Media & listing**.
4. Isi harga cash dan harga paket kredit.
5. Isi media, video walkaround, dan deskripsi iklan.
6. Pilih channel publikasi.
7. Centang **Publikasikan sekarang**.
8. Tekan **Simpan listing**.

Hasil: status menjadi `PUBLISHED`.

Pemilihan channel hanya dicatat sebagai administrasi. Aplikasi tidak mengirim iklan secara otomatis ke API marketplace eksternal.

### Tahap M — Booking customer

Masih menggunakan akun Sales & Marketing:

1. Buka unit berstatus **Siap jual** atau **Published**.
2. Tekan **Booking customer**.
3. Isi nama, nomor WhatsApp, NIK, dan alamat pembeli.
4. Pilih skema `CASH` atau `CREDIT`.
5. Isi harga jual final dan down payment.
6. Untuk kredit, vendor leasing dan tenor wajib diisi.
7. Tekan **Simpan booking**.

Hasil: status menjadi `BOOKED`. Pada tahap ini unit belum dianggap terjual atau sudah diserahkan.

## 6. Cabang penjualan cash

Untuk booking dengan skema `CASH`:

1. Buka unit berstatus **Booking**.
2. Tekan **Mulai pembayaran**.
3. Konfirmasi proses.
4. Status menjadi `CASH_CONFIRMED`.
5. Tekan **Tandai deal**.
6. Status menjadi `DEAL`.

Lanjutkan ke bagian **Penjadwalan dan penyelesaian delivery**.

## 7. Cabang penjualan kredit

Untuk booking dengan skema `CREDIT`:

1. Buka unit berstatus **Booking**.
2. Tekan **Mulai pembayaran**.
3. Status menjadi `SURVEY_FINANCE`.
4. Setelah survey customer dan kendaraan selesai, tekan **Survey selesai**.
5. Status menjadi `FINANCE_PROCESS`.
6. Setelah leasing memberikan keputusan, tekan **Keputusan finance**.
7. Pilih **Disetujui** atau **Ditolak/revisi**.
8. Isi nomor referensi leasing dan catatan.
9. Simpan keputusan.

Jika finance disetujui:

- Status menjadi `FINANCE_APPROVED`.
- Tekan **Tandai deal**.
- Status menjadi `DEAL`.

Jika finance ditolak atau memerlukan revisi:

- Status kembali menjadi `BOOKED`.
- Data booking dapat diproses ulang sesuai tindak lanjut customer.

## 8. Penjadwalan dan penyelesaian delivery

Masih menggunakan akun Sales & Marketing:

### Menjadwalkan delivery

1. Buka unit berstatus **Deal**.
2. Tekan **Jadwalkan delivery**.
3. Isi tanggal dan waktu penyerahan.
4. Isi catatan penyerahan.
5. Tekan **Simpan jadwal**.

Hasil: status menjadi `DELIVERY_SCHEDULED`.

### Menyelesaikan delivery

1. Setelah kendaraan benar-benar diterima customer, buka unit tersebut.
2. Tekan **Selesaikan delivery**.
3. Isi catatan penerimaan.
4. Tekan **Konfirmasi unit diterima**.

Hasil: status akhir menjadi `SOLD_DELIVERED`.

Jangan menyelesaikan delivery sebelum unit benar-benar diserahkan. Status `SOLD_DELIVERED` digunakan untuk laporan omzet dan profit.

## 9. Dokumen transaksi dan greeting

Setelah status menjadi `SOLD_DELIVERED`, Sales mendapatkan dua tindakan tambahan.

### Dokumen transaksi

1. Tekan **Dokumen transaksi**.
2. Pilih dokumen:
   - SPK.
   - Kwitansi.
   - BASTK.
3. Dokumen akan dibuka di tab baru.
4. Gunakan fungsi cetak browser untuk mencetak atau menyimpan sebagai PDF.

### Delivery greeting

1. Tekan **Greeting**.
2. Ambil foto customer melalui kamera atau unggah foto dari perangkat.
3. Isi rating kepuasan.
4. Isi catatan customer.
5. Centang persetujuan penyimpanan dan publikasi media.
6. Tekan **Simpan greeting**.

Media greeting tidak dapat disimpan tanpa persetujuan customer.

## 10. Sales & CRM

Menu **Sales & CRM** digunakan untuk mencatat calon customer sebelum transaksi.

1. Tekan **Lead**.
2. Isi nama, nomor WhatsApp, sumber lead, unit yang diminati, dan catatan.
3. Simpan lead.
4. Gunakan tab untuk melihat lead berdasarkan tahap.
5. Tekan **Ubah status**.
6. Pilih status tujuan dan isi catatan tindak lanjut.
7. Tekan **Simpan perubahan**.

```text
NEW / FOLLOW_UP / TEST_DRIVE / SPK_ISSUED / CLOSED / CANCELLED
```

Status dapat dipilih langsung tanpa harus bergerak berurutan. Lead berstatus Closed atau Cancel tetap dapat diubah kembali ke status aktif apabila customer melanjutkan proses.

CRM dan transaksi unit merupakan data terpisah. Closing lead tidak otomatis menandai unit sebagai terjual; flow booking dan delivery tetap harus dijalankan.

## 11. Kalender

Kalender dapat dibuka dari menu **Home**.

Agenda yang dapat dibuat:

- Inspeksi.
- Repair.
- Jatuh tempo pajak.
- Test drive.
- Delivery.

Pilih unit terkait agar agenda mudah ditelusuri dari aktivitas operasional.

## 12. Laporan dan audit

Login sebagai Owner untuk membuka:

- **Laporan**: omzet, HPP, profit, dan margin unit yang sudah `SOLD_DELIVERED`.
- **Audit trail**: riwayat login, pembuatan data, perubahan status, approval, upload, dan tindakan penting lainnya.
- **User management**: pembuatan akun, aktivasi akun, role, dan nomor WhatsApp.

Rumus laporan:

```text
HPP = harga beli + total realisasi biaya repair
Profit = harga jual final - HPP
Margin = profit / harga jual final × 100%
```

### Export laporan lengkap

Pada halaman **Laporan**, Owner dapat memilih:

- **Export PDF**: menghasilkan satu halaman ringkasan dan tepat satu halaman landscape untuk setiap unit. Setiap halaman unit memuat identitas, approval, inspeksi, pembayaran, repair, Document QC, listing, penjualan, audit ringkas, dan galeri foto.
- **Export Excel**: menghasilkan workbook dengan sheet Ringkasan, Unit, Alur & Approval, Inspeksi, Pekerjaan Repair, Dokumen, Penjualan, Tautan Foto, dan Audit Timeline. Foto tidak ditempelkan ke Excel; kolom link dapat ditekan untuk membuka foto.

Tekan tombol export dan tunggu hingga browser mengunduh file. Waktu pembuatan PDF dapat lebih lama jika jumlah unit dan foto banyak.

## 13. Aturan penting sistem

1. Status unit tidak dapat dilompati.
2. Unit baru wajib mempunyai satu foto cover dari tahap Sourcing.
3. Foto cover tidak dihitung sebagai foto inspeksi.
4. Legal precheck wajib selesai sebelum checker ditugaskan.
5. Inspeksi wajib mempunyai tepat delapan foto.
6. Hanya HOD yang mengambil keputusan pembelian operasional.
7. Nominal voucher harus sama dengan harga yang disetujui HOD.
8. Bukti pembayaran wajib diunggah sebelum unit dianggap dibeli.
9. Repair 100% memerlukan foto before dan after.
10. Repair QC harus lulus sebelum Document QC.
11. Listing dan booking hanya tersedia setelah Document QC lulus.
12. Booking tidak langsung mengubah unit menjadi terjual.
13. Finance kredit harus melewati survey dan approval.
14. Unit baru dianggap terjual setelah delivery selesai.
15. Greeting dengan media memerlukan consent customer.

## 14. Skenario pengujian paling cepat

Untuk menguji satu unit dari awal sampai akhir, gunakan urutan login berikut:

```text
1. owner@lbauto.id       → atur nomor WhatsApp user
2. krisna@lbauto.id      → input unit dan satu foto cover
3. ciprut@lbauto.id      → Initial QC
4. legal@lbauto.id       → legal precheck
5. ciprut@lbauto.id      → assign checker
6. checker@lbauto.id     → inspeksi dan delapan foto
7. hod@lbauto.id         → approval pembelian
8. krisna@lbauto.id      → voucher dan bukti pembayaran
9. workshop@lbauto.id    → handover dan repair
10. hod@lbauto.id        → Repair QC
11. legal@lbauto.id      → Document QC
12. sales@lbauto.id      → listing dan booking
13. sales@lbauto.id      → cash/finance, deal, dan delivery
14. sales@lbauto.id      → dokumen transaksi dan greeting
15. owner@lbauto.id      → periksa laporan, audit, dan log WA
```

## 15. Pemecahan masalah

### Tampilan masih versi lama

Versi PWA terbaru akan memeriksa pembaruan service worker secara otomatis. Tutup aplikasi atau tab, lalu buka kembali. Jika desktop masih menampilkan versi lama, lakukan hard refresh:

- Windows/Linux: `Ctrl + Shift + R`
- macOS: `Command + Shift + R`

Pada mobile yang tidak menyediakan hard refresh:

1. Tutup seluruh tab LB AUTO atau tutup PWA dari recent apps.
2. Buka kembali alamat aplikasi.
3. Jika masih lama, buka sekali dengan parameter baru, misalnya `https://alamat-aplikasi/?refresh=1`.
4. Sebagai langkah terakhir, hapus data situs LB AUTO dari pengaturan browser lalu login kembali.

Menghapus data situs akan menghapus sesi login pada perangkat tersebut, tetapi tidak menghapus data unit di server.

### Tombol tindakan tidak muncul

Periksa:

1. Role akun yang sedang login.
2. Status unit saat ini.
3. Apakah tahap sebelumnya sudah diselesaikan.

Tombol hanya ditampilkan untuk role dan status yang berhak melakukan tindakan tersebut.

### Notifikasi WhatsApp tidak terkirim

Login sebagai Owner, lalu periksa:

1. Nomor WhatsApp role tujuan sudah diatur.
2. Nomor menggunakan format `62`.
3. Integrasi Fonnte aktif pada `.env`.
4. Token Fonnte masih valid.
5. Ikon lonceng untuk melihat status dan pesan kegagalan.

### Foto gagal diunggah

Pastikan:

- Format file JPG, PNG, atau WebP.
- Ukuran tidak melebihi 8 MB per file.
- Browser mempunyai izin kamera jika mengambil foto langsung.
- Server masih berjalan.

Pastikan juga jenis foto sesuai tahapnya:

- Sourcing: tepat satu foto cover.
- Inspeksi: tepat delapan foto pada delapan field berbeda.
- Pembayaran: satu bukti pembayaran.
- Repair: foto before dan after.
- Greeting: satu foto customer dengan consent.

### Server tidak dapat dibuka

Jalankan kembali:

```bash
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Pastikan terminal tetap terbuka selama aplikasi digunakan.
