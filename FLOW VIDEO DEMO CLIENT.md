# Flow Pembuatan Video Demo LB AUTO untuk Client

Dokumen ini menjadi panduan produksi video demo aplikasi LB AUTO dari persiapan, perekaman, narasi, hingga hasil akhir. Target video adalah menunjukkan bahwa setiap unit dikontrol oleh role, approval, bukti, dan status yang jelas dari sourcing sampai delivery.

## 1. Tujuan video

Setelah menonton video, client harus memahami bahwa:

1. LB AUTO mempunyai satu sistem untuk seluruh operasional showroom.
2. Setiap bagian hanya melihat dan menjalankan tindakan sesuai role.
3. Unit tidak dapat melompati proses atau approval.
4. Foto, dokumen, biaya, dan audit trail tersimpan dalam satu unit.
5. Approval penting dapat memicu notifikasi WhatsApp.
6. Penjualan cash dan kredit memiliki alur yang jelas.
7. Unit baru dianggap terjual setelah delivery benar-benar selesai.

Pesan utama video:

> LB AUTO menghubungkan pembelian, inspeksi, legal, workshop, sales, dan management dalam satu alur yang terkontrol.

## 2. Format video yang disarankan

Gunakan format berikut:

- Durasi utama: 12–15 menit.
- Resolusi: 1920 × 1080 piksel.
- Frame rate: 30 fps.
- Format akhir: MP4 H.264.
- Tampilan aplikasi: browser dalam ukuran mobile.
- Bahasa narasi: Bahasa Indonesia.
- Gaya: tenang, profesional, langsung ke manfaat bisnis.
- Musik: instrumental premium dengan volume rendah dan tanpa vokal.

Jangan merekam seluruh flow dalam satu pengambilan. Rekam per bab, kemudian gabungkan saat editing. Cara ini memudahkan pergantian akun dan pengulangan apabila ada salah klik.

## 3. Struktur video akhir

| Waktu | Bab | Isi utama |
| --- | --- | --- |
| 00:00–00:30 | Opening | Masalah operasional dan solusi LB AUTO |
| 00:30–01:20 | Home & RBAC | Dashboard mobile, menu, role, dan WhatsApp |
| 01:20–02:10 | Sourcing | Input unit baru oleh PIC Pembelian |
| 02:10–03:10 | Initial & Legal QC | Initial QC dan legal precheck |
| 03:10–04:30 | Inspeksi | Assign checker, pemeriksaan, dan delapan foto |
| 04:30–05:30 | Approval & Pembayaran | Keputusan HOD, voucher, dan bukti bayar |
| 05:30–07:20 | Workshop | Handover, repair per panel, foto, dan Repair QC |
| 07:20–08:10 | Document QC | Pemeriksaan dokumen dan gate siap jual |
| 08:10–09:10 | Listing & CRM | Listing kendaraan dan pengelolaan lead |
| 09:10–11:20 | Penjualan | Booking, cash/kredit, finance, dan deal |
| 11:20–12:30 | Delivery | Jadwal, penyelesaian delivery, dan greeting |
| 12:30–13:30 | Management | Laporan, audit trail, dan log WhatsApp |
| 13:30–14:00 | Closing | Ringkasan manfaat dan ajakan diskusi |

Apabila video perlu lebih pendek, gunakan versi 7–8 menit dengan mempercepat bagian pengisian form dan fokus pada perubahan status.

## 4. Persiapan sebelum recording

### 4.1 Jalankan aplikasi

Jalankan server:

```bash
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Buka aplikasi:

```text
http://127.0.0.1:8000
```

Pastikan endpoint berikut memberikan status `ok`:

```text
http://127.0.0.1:8000/api/health
```

### 4.2 Bersihkan tampilan browser

Sebelum recording:

1. Tutup bookmark bar.
2. Matikan notifikasi browser dan desktop.
3. Tutup tab yang tidak digunakan.
4. Gunakan zoom browser 100%.
5. Gunakan DevTools Device Toolbar atau jendela browser sempit dengan lebar sekitar 390–430 piksel.
6. Gunakan hard refresh agar service worker memuat versi terbaru.
7. Pastikan kursor tidak menggunakan efek yang berlebihan.

Ukuran mobile yang disarankan:

```text
Width: 390 px
Height: 844 px
Device pixel ratio: 1 atau 2
```

Untuk beberapa bagian seperti laporan dan user management, rekam satu cuplikan tambahan dalam ukuran desktop agar responsivitas aplikasi terlihat.

### 4.3 Siapkan akun

Semua akun demo menggunakan password:

```text
LBAuto123!
```

| Role | Email |
| --- | --- |
| Owner | `owner@lbauto.id` |
| PIC Pembelian | `krisna@lbauto.id` |
| Inspection Leader | `ciprut@lbauto.id` |
| PIC Legal | `legal@lbauto.id` |
| Field Checker | `checker@lbauto.id` |
| HOD | `hod@lbauto.id` |
| PIC Workshop | `workshop@lbauto.id` |
| Sales & Marketing | `sales@lbauto.id` |

Jangan menampilkan password produksi, token Fonnte, file `.env`, atau isi database dalam video.

### 4.4 Siapkan data unit contoh

Gunakan satu unit yang mudah dikenali sepanjang video:

| Data | Nilai contoh |
| --- | --- |
| Merek | Porsche |
| Model | Macan S |
| Tahun | 2023 |
| Warna | Carrara White |
| Nomor polisi | B 9090 LBA |
| Transmisi | AT |
| Odometer | 8.900 km |
| Nomor rangka | WP1ZZZ95ZPLB09090 |
| Nomor mesin | DGM09090 |
| Sumber | Perorangan |
| Penjual | Demo Seller |
| Nomor penjual | 081234567890 |
| Lokasi | Jakarta Selatan |
| Harga penawaran | Rp1.550.000.000 |
| Target harga | Rp1.490.000.000 |
| Harga deal pembelian | Rp1.490.000.000 |
| Harga jual | Rp1.650.000.000 |

Jika nomor polisi tersebut sudah pernah digunakan, ganti menjadi nomor unik, misalnya `B 9091 LBA`.

### 4.5 Siapkan file foto

Buat satu folder khusus sebelum merekam:

```text
demo-assets/
├── 01-depan.jpg
├── 02-belakang.jpg
├── 03-kanan.jpg
├── 04-kiri.jpg
├── 05-mesin.jpg
├── 06-interior.jpg
├── 07-rangka.jpg
├── 08-odometer.jpg
├── repair-before.jpg
├── repair-after.jpg
├── bukti-pembayaran.jpg
└── delivery-greeting.jpg
```

Gunakan foto landscape yang bersih dan konsisten. Hindari data customer asli, nomor rekening asli, atau dokumen identitas asli dalam video demo.

### 4.6 Siapkan data transaksi

Data customer contoh:

| Data | Nilai contoh |
| --- | --- |
| Nama | Adrian Wijaya |
| WhatsApp | 081200001111 |
| NIK | 3174000000000001 |
| Alamat | Jakarta Selatan |
| Skema | CREDIT |
| Leasing | BCA Finance |
| Tenor | 36 bulan |
| Down payment | Rp500.000.000 |
| Harga final | Rp1.650.000.000 |
| Referensi leasing | BCAF-DEMO-2026-001 |

Gunakan data fiktif dan tampilkan label kecil “Data demonstrasi” saat editing.

## 5. Metode recording yang paling aman

Gunakan pola ini untuk setiap bab:

1. Rekam layar tanpa narasi.
2. Lakukan klik dengan tempo sedikit lebih lambat dari penggunaan normal.
3. Diam selama satu detik sebelum dan sesudah klik penting.
4. Pastikan perubahan status terlihat selama dua sampai tiga detik.
5. Rekam voice-over setelah seluruh visual selesai.
6. Potong waktu mengetik yang terlalu lama menjadi 2–3 detik.
7. Tambahkan teks role aktif di pojok layar.

Contoh label role:

```text
PIC PEMBELIAN
INSPECTION LEADER
PIC LEGAL
FIELD CHECKER
HOD
PIC WORKSHOP
SALES & MARKETING
OWNER
```

Setiap kali berganti akun, gunakan transisi singkat 0,3–0,5 detik dan tampilkan nama role. Client tidak perlu melihat proses mengetik email dan password secara penuh pada setiap pergantian.

## 6. Storyboard dan narasi lengkap

## Bab 1 — Opening

Durasi: 00:00–00:30

### Visual

1. Tampilkan logo LB AUTO pada latar putih.
2. Potong ke halaman login.
3. Tampilkan tiga teks singkat secara berurutan:
   - Satu flow operasional.
   - Approval berbasis role.
   - Dari sourcing sampai delivery.

### Narasi

> Operasional showroom melibatkan banyak bagian, mulai dari pembelian, inspeksi, legal, workshop, hingga sales. LB AUTO menyatukan seluruh proses tersebut dalam satu aplikasi mobile-first dengan status, approval, bukti, dan audit trail yang jelas.

### Catatan editing

- Jangan menggunakan animasi logo berlebihan.
- Gunakan fade sederhana.
- Musik mulai masuk perlahan.

## Bab 2 — Home, RBAC, dan WhatsApp

Durasi: 00:30–01:20

### Akun

```text
owner@lbauto.id
```

### Visual

1. Login sebagai Owner.
2. Tampilkan Home selama tiga detik.
3. Scroll perlahan pada metrik, komposisi stok, dan menu.
4. Buka **User management**.
5. Tampilkan daftar role Legal dan HOD.
6. Tekan **Atur WA** pada salah satu user.
7. Jangan menyimpan nomor asli; cukup tunjukkan form.
8. Tutup modal.
9. Tekan ikon lonceng dan tampilkan log notifikasi.

### Narasi

> Home memberikan ringkasan stok dan aktivitas operasional dalam tampilan yang nyaman digunakan dari ponsel. Setiap pengguna mempunyai role tersendiri. Owner dapat mengatur nomor WhatsApp approver, sedangkan sistem mencatat status pengiriman notifikasi Fonnte untuk setiap proses yang membutuhkan tindakan.

### Teks layar

```text
RBAC: setiap role hanya menjalankan tugasnya
Approval notification melalui WhatsApp
```

## Bab 3 — Sourcing unit

Durasi: 01:20–02:10

### Akun

```text
krisna@lbauto.id
```

### Visual

1. Tampilkan label **PIC PEMBELIAN**.
2. Buka menu **Sourcing**.
3. Isi form menggunakan data Porsche Macan S.
4. Percepat bagian mengetik.
5. Tekan **Simpan unit**.
6. Tahan tampilan detail unit.
7. Zoom ringan pada badge `SOURCED` dan ID unit.

### Narasi

> Flow dimulai dari PIC Pembelian. Informasi penjual, identitas kendaraan, odometer, harga penawaran, dan target pembelian dicatat dalam satu form. Setelah disimpan, sistem membuat ID unit dan mengubah status menjadi Sourced.

### Teks layar

```text
Status: SOURCED
Notifikasi: Initial QC diperlukan
```

## Bab 4 — Initial QC dan legal precheck

Durasi: 02:10–03:10

### Bagian A — Inspection Leader

#### Akun

```text
ciprut@lbauto.id
```

#### Visual

1. Buka menu **Inspeksi**.
2. Pilih Porsche Macan S.
3. Tekan **Initial QC**.
4. Pilih **Lolos**.
5. Isi catatan: `Unit sesuai kriteria awal showroom`.
6. Simpan.
7. Tampilkan status `INITIAL_QC`.

#### Narasi

> Inspection Leader melakukan penyaringan awal. Jika unit tidak sesuai kriteria, proses dapat dihentikan sejak tahap ini. Unit yang lolos diteruskan kepada PIC Legal.

### Bagian B — PIC Legal

#### Akun

```text
legal@lbauto.id
```

#### Visual

1. Tampilkan label **PIC LEGAL**.
2. Buka unit yang sama.
3. Tekan **Pemeriksaan legal**.
4. Centang STNK, BPKB, nomor rangka, nomor mesin, dan pajak.
5. Isi catatan: `Identitas kendaraan dan dokumen sesuai`.
6. Simpan.
7. Tampilkan status `LEGAL_PRECHECK`.

#### Narasi

> Sebelum inspeksi lapangan, PIC Legal memastikan dokumen dasar serta identitas kendaraan sesuai. Seluruh pemeriksaan merupakan gate wajib dan tidak dapat dilewati.

## Bab 5 — Assignment dan inspeksi delapan foto

Durasi: 03:10–04:30

### Bagian A — Assign checker

#### Akun

```text
ciprut@lbauto.id
```

#### Visual

1. Buka unit berstatus **Legal cleared**.
2. Tekan **Tugaskan checker**.
3. Pilih Rendi Checker.
4. Simpan.
5. Tampilkan status `CHECKER_ASSIGNED`.

#### Narasi

> Setelah legal precheck lolos, Inspection Leader menugaskan unit kepada Field Checker tertentu. Checker hanya dapat menangani unit yang memang menjadi tugasnya.

### Bagian B — Inspeksi lapangan

#### Akun

```text
checker@lbauto.id
```

#### Visual

1. Buka tugas inspeksi.
2. Isi skor body `94`.
3. Isi mesin normal, oli kering, kaki-kaki normal, tanpa banjir dan tanpa tabrak besar.
4. Isi catatan: `Unit sangat terawat, terdapat baret ringan pada bumper`.
5. Tampilkan semua field foto.
6. Unggah delapan foto yang sudah disiapkan.
7. Tekan **Kirim laporan**.
8. Buka tab **Inspeksi** pada detail unit.
9. Tampilkan status `REPORT_SUBMITTED`.

#### Narasi

> Field Checker mengisi kondisi kendaraan dan wajib melampirkan delapan foto standar. Foto depan, belakang, kedua sisi, mesin, interior, nomor rangka, dan odometer memastikan laporan mempunyai bukti visual yang konsisten.

### Tips editing

- Tampilkan proses unggah foto pertama secara normal.
- Percepat tujuh foto berikutnya menjadi montase dua sampai tiga detik.
- Tampilkan teks `8/8 foto lengkap`.

## Bab 6 — Approval HOD dan pembayaran

Durasi: 04:30–05:30

### Bagian A — Keputusan HOD

#### Akun

```text
hod@lbauto.id
```

#### Visual

1. Buka unit berstatus **Review HOD**.
2. Tampilkan tab inspeksi dan ringkasan harga.
3. Tekan **Keputusan HOD**.
4. Pilih **Deal beli**.
5. Isi harga `1.490.000.000`.
6. Simpan.
7. Tampilkan status `HOD_APPROVED`.

#### Narasi

> Laporan checker tidak langsung membuat unit terbeli. HOD memeriksa hasil inspeksi dan menetapkan keputusan serta harga pembelian final.

### Bagian B — Voucher dan bukti pembayaran

#### Akun

```text
krisna@lbauto.id
```

#### Visual

1. Tekan **Buat voucher**.
2. Isi nomor voucher unik, misalnya `PV-DEMO-2026-001`.
3. Isi nominal sesuai harga HOD.
4. Pilih transfer bank.
5. Simpan dan tunjukkan status `PAYMENT_PENDING`.
6. Tekan **Konfirmasi pembayaran**.
7. Unggah `bukti-pembayaran.jpg`.
8. Simpan dan tunjukkan status `PURCHASED_PAID`.

#### Narasi

> PIC Pembelian membuat voucher dengan nominal yang harus sama dengan approval HOD. Status pembelian baru selesai setelah bukti pembayaran benar-benar diunggah.

## Bab 7 — Workshop dan Repair QC

Durasi: 05:30–07:20

### Bagian A — Handover dan pekerjaan repair

#### Akun

```text
workshop@lbauto.id
```

#### Visual

1. Buka menu **Workshop**.
2. Pilih Porsche Macan S.
3. Tekan **Terima unit**.
4. Isi odometer `8905`.
5. Isi catatan: `Unit diterima lengkap dan kondisi sesuai laporan`.
6. Simpan.
7. Tekan **Update repair**.
8. Isi vendor `Workshop LB AUTO`.
9. Pilih tahap `Clear coat & polish`.
10. Isi pekerjaan:
    - Kategori: Bumper Repair.
    - Panel: Bumper depan.
    - Progres: 100%.
    - Estimasi: Rp5.000.000.
    - Realisasi: Rp4.500.000.
11. Unggah foto before dan after.
12. Simpan.
13. Tampilkan status `REPAIR_QC`.

#### Narasi

> PIC Workshop terlebih dahulu mengonfirmasi serah-terima fisik. Pekerjaan kemudian dicatat per panel, termasuk progres, estimasi, realisasi biaya, serta foto before dan after. Ketika semua pekerjaan mencapai seratus persen, unit belum langsung siap jual, tetapi masuk ke Repair QC.

### Bagian B — Repair QC oleh HOD

#### Akun

```text
hod@lbauto.id
```

#### Visual

1. Buka unit berstatus **Repair QC**.
2. Tampilkan detail repair.
3. Tekan **Approval Repair QC**.
4. Pilih **Lulus QC**.
5. Isi catatan: `Hasil repair rapi dan sesuai standar showroom`.
6. Simpan.
7. Tampilkan status `DOCUMENT_QC`.

#### Narasi

> HOD memberikan approval akhir atas kualitas repair. Jika hasil belum sesuai, unit dikembalikan ke workshop. Unit yang lolos baru diteruskan ke Document QC.

## Bab 8 — Document QC

Durasi: 07:20–08:10

### Akun

```text
legal@lbauto.id
```

### Visual

1. Buka menu **Workshop**.
2. Pilih unit berstatus **Document QC**.
3. Tekan **Document QC**.
4. Pilih STNK asli.
5. Isi tanggal pajak.
6. Pilih BPKB asli dan isi nomornya.
7. Pilih faktur lengkap.
8. Centang kwitansi bermaterai.
9. Centang fotokopi KTP pemilik.
10. Simpan.
11. Tampilkan status `READY_TO_SELL`.

### Narasi

> Document QC adalah gate terakhir sebelum pemasaran. Listing tidak dapat dibuat apabila STNK, BPKB, faktur, kwitansi, atau identitas pemilik belum lengkap.

### Teks layar

```text
Repair QC Passed
Document QC Passed
READY_TO_SELL
```

## Bab 9 — Listing dan CRM

Durasi: 08:10–09:10

### Akun

```text
sales@lbauto.id
```

### Bagian A — Listing

#### Visual

1. Buka unit berstatus **Siap jual**.
2. Tekan **Media & listing**.
3. Isi harga cash `1.650.000.000`.
4. Isi harga kredit `1.675.000.000`.
5. Isi deskripsi singkat.
6. Pilih Instagram, OLX, dan Facebook Marketplace.
7. Centang publikasi.
8. Simpan.
9. Tampilkan status `PUBLISHED` dan foto asli mobil pada inventory.

#### Narasi

> Setelah semua QC lulus, Sales menyiapkan harga, media, deskripsi, dan channel publikasi. Channel marketplace dicatat sebagai kontrol operasional pemasaran.

### Bagian B — CRM

#### Visual

1. Buka menu **Sales & CRM**.
2. Tampilkan tab lead.
3. Tambahkan satu lead singkat atau gunakan lead demo.
4. Pindahkan status dari Lead Baru ke Follow Up.
5. Tampilkan foto kendaraan pada card customer.

#### Narasi

> Modul CRM mencatat sumber prospect, unit yang diminati, catatan follow-up, test drive, SPK, hingga closing. Tampilan tab membantu Sales berfokus pada tahap customer yang sedang ditangani.

## Bab 10 — Booking dan proses kredit

Durasi: 09:10–11:20

Gunakan flow kredit karena menampilkan proses paling lengkap. Tambahkan catatan singkat bahwa transaksi cash melewati jalur yang lebih sederhana.

### Bagian A — Booking

#### Visual

1. Kembali ke unit Porsche Macan S.
2. Tekan **Booking customer**.
3. Isi data Adrian Wijaya.
4. Pilih `CREDIT`.
5. Isi BCA Finance dan tenor 36 bulan.
6. Isi down payment dan harga final.
7. Simpan.
8. Tampilkan status `BOOKED`.

#### Narasi

> Booking menyimpan data customer, skema pembayaran, harga final, down payment, vendor leasing, dan tenor. Pada tahap ini unit belum dianggap terjual atau sudah diserahkan.

### Bagian B — Survey dan finance approval

#### Visual

1. Tekan **Mulai pembayaran**.
2. Tampilkan status `SURVEY_FINANCE`.
3. Tekan **Survey selesai**.
4. Tampilkan status `FINANCE_PROCESS`.
5. Tekan **Keputusan finance**.
6. Pilih **Disetujui**.
7. Isi referensi `BCAF-DEMO-2026-001`.
8. Isi catatan: `Survey dan pengajuan disetujui`.
9. Simpan.
10. Tampilkan status `FINANCE_APPROVED`.
11. Tekan **Tandai deal**.
12. Tampilkan status `DEAL`.

#### Narasi

> Transaksi kredit melewati survey, proses finance, dan keputusan leasing. Vendor serta nomor referensi tersimpan pada transaksi. Setelah finance disetujui, Sales mengonfirmasi deal untuk membuka penjadwalan delivery.

### Penjelasan cash

Tampilkan overlay selama tiga detik:

```text
Flow cash:
BOOKED → CASH_CONFIRMED → DEAL
```

Narasi tambahan:

> Untuk transaksi cash, sistem bergerak dari booking ke cash confirmed, kemudian deal tanpa tahap survey leasing.

## Bab 11 — Delivery dan greeting

Durasi: 11:20–12:30

### Visual

1. Tekan **Jadwalkan delivery**.
2. Pilih tanggal dan waktu demo.
3. Isi catatan: `Serah-terima di showroom LB AUTO`.
4. Simpan.
5. Tampilkan status `DELIVERY_SCHEDULED`.
6. Tekan **Selesaikan delivery**.
7. Isi catatan: `Unit diterima customer dalam kondisi baik`.
8. Konfirmasi.
9. Tampilkan status `SOLD_DELIVERED`.
10. Tekan **Dokumen transaksi**.
11. Tampilkan SPK, kwitansi, dan BASTK secara cepat.
12. Kembali ke detail unit.
13. Tekan **Greeting**.
14. Unggah `delivery-greeting.jpg`.
15. Pilih rating lima.
16. Centang consent customer.
17. Simpan.

### Narasi

> Deal belum menandai unit sebagai selesai. Sales terlebih dahulu menjadwalkan delivery dan baru mengonfirmasinya setelah kendaraan benar-benar diterima customer. Setelah itu, SPK, kwitansi, BASTK, dan media greeting dapat dikelola dari unit yang sama.

### Teks layar

```text
Unit selesai hanya setelah delivery dikonfirmasi
Status akhir: SOLD_DELIVERED
```

## Bab 12 — Laporan, audit, dan notifikasi

Durasi: 12:30–13:30

### Akun

```text
owner@lbauto.id
```

### Visual

1. Tampilkan Home yang sudah diperbarui.
2. Buka **Laporan**.
3. Tunjukkan harga jual, HPP, profit, dan margin.
4. Buka **Audit trail**.
5. Scroll beberapa aktivitas unit yang baru dibuat.
6. Tekan ikon lonceng.
7. Tampilkan log notifikasi approval.

### Narasi

> Management memperoleh visibilitas akhir terhadap omzet, HPP, biaya repair, profit, dan margin. Seluruh tindakan penting tercatat pada audit trail, sementara status notifikasi WhatsApp dapat dipantau dari log pengiriman.

### Teks layar

```text
HPP = Harga beli + biaya repair
Profit = Harga jual - HPP
Full audit trail
```

## Bab 13 — Closing

Durasi: 13:30–14:00

### Visual

1. Kembali ke Home.
2. Tampilkan komposisi stok dan menu.
3. Potong ke detail Porsche Macan S berstatus `SOLD_DELIVERED`.
4. Akhiri dengan logo LB AUTO.

### Narasi

> Dengan LB AUTO, setiap unit bergerak melalui proses yang konsisten, setiap approval mempunyai penanggung jawab, dan seluruh data dapat ditelusuri dari sourcing hingga delivery. Sistem ini membantu tim bekerja lebih rapi sekaligus memberikan management kontrol yang lebih kuat terhadap operasional showroom.

### Closing text

```text
LB AUTO
One controlled flow, from sourcing to delivery.
```

## 7. Shot list recording

Rekam file per bab agar editing mudah:

```text
01-opening.mp4
02-owner-home-rbac.mp4
03-sourcing.mp4
04-initial-qc.mp4
05-legal-precheck.mp4
06-assign-checker.mp4
07-inspection.mp4
08-hod-purchase.mp4
09-payment.mp4
10-repair-handover.mp4
11-repair-work.mp4
12-repair-qc.mp4
13-document-qc.mp4
14-listing.mp4
15-crm.mp4
16-booking.mp4
17-finance.mp4
18-delivery.mp4
19-greeting.mp4
20-report-audit.mp4
21-closing.mp4
```

Untuk setiap file:

- Sisakan dua detik kosong pada awal dan akhir.
- Jangan menghentikan recording tepat setelah klik.
- Pastikan toast sukses sempat terlihat.
- Pastikan badge status baru terekam.

## 8. Panduan voice-over

### Cara membaca

- Kecepatan: 125–145 kata per menit.
- Gunakan intonasi tenang dan percaya diri.
- Beri jeda setelah menyebut perubahan status.
- Hindari membaca semua isi form.
- Jelaskan manfaat proses, bukan hanya nama tombol.

Contoh yang kurang efektif:

> Sekarang saya klik tombol ini, lalu saya isi field ini.

Contoh yang lebih efektif:

> Nominal voucher dikunci sesuai approval HOD sehingga nilai pembayaran tetap konsisten dengan keputusan pembelian.

### Istilah yang perlu konsisten

Gunakan penyebutan berikut sepanjang video:

- “Unit”, bukan “barang”.
- “PIC Pembelian”, bukan “admin beli”.
- “Field Checker”, bukan “surveyor”, kecuali menjelaskan konteks.
- “Repair QC” dan “Document QC”.
- “Customer”, jika mengikuti bahasa operasional LB AUTO.
- “Delivery”, bukan bergantian dengan terlalu banyak istilah lain.

## 9. Panduan editing

### Transisi

- Gunakan cut biasa untuk perpindahan aksi.
- Gunakan fade singkat saat berganti bab.
- Hindari transisi 3D, putaran, atau efek mencolok.

### Zoom dan highlight

Gunakan zoom hanya untuk:

- Badge status.
- Tombol approval.
- Delapan foto inspeksi.
- Biaya repair.
- Vendor leasing.
- Status `SOLD_DELIVERED`.
- Profit pada laporan.

Gunakan highlight outline merah LB AUTO dengan ketebalan tipis. Jangan menutup elemen aplikasi.

### Teks layar

Batasi satu overlay maksimal dua baris. Gunakan warna:

- Putih sebagai background.
- Hitam atau abu gelap untuk teks.
- Merah logo LB AUTO untuk highlight.
- Hijau hanya untuk status sukses.

Hindari gradient dan animasi teks berlebihan.

### Informasi sensitif

Blur atau potong apabila terlihat:

- Token Fonnte.
- Nomor rekening asli.
- NIK atau alamat customer asli.
- Nomor WhatsApp pribadi.
- File `.env`.
- Password selain akun demo lokal.

## 10. Versi video singkat 7–8 menit

Jika client hanya membutuhkan overview, gunakan struktur berikut:

| Durasi | Isi |
| --- | --- |
| 00:00–00:25 | Opening dan masalah bisnis |
| 00:25–01:00 | Home, mobile UI, dan RBAC |
| 01:00–02:30 | Sourcing sampai inspeksi delapan foto |
| 02:30–03:30 | HOD approval, voucher, dan pembayaran |
| 03:30–04:40 | Repair per panel, before/after, dan QC |
| 04:40–05:20 | Document QC dan listing gate |
| 05:20–06:40 | Booking, finance/cash, dan deal |
| 06:40–07:20 | Delivery dan greeting |
| 07:20–08:00 | Laporan, audit, WhatsApp, dan closing |

Pada versi singkat:

- Potong proses login dan tampilkan label role saja.
- Percepat pengisian form 4–6 kali.
- Tampilkan hanya satu contoh foto inspeksi lalu montase delapan foto.
- Ringkas CRM menjadi cuplikan lima detik.
- Gunakan voice-over untuk menjelaskan cabang cash tanpa merekam transaksi kedua.

## 11. Checklist sebelum export

### Aplikasi

- [ ] Semua badge status terlihat jelas.
- [ ] Tidak ada error toast dalam rekaman final.
- [ ] Unit yang digunakan konsisten dari awal sampai akhir.
- [ ] Harga beli, repair, dan harga jual konsisten.
- [ ] Nama role tampil setiap pergantian akun.
- [ ] Flow kredit atau cash dijelaskan dengan benar.
- [ ] Unit berakhir pada `SOLD_DELIVERED`.

### Visual

- [ ] Logo tidak terpotong.
- [ ] Tampilan mobile berada di tengah frame.
- [ ] Teks browser dapat dibaca pada resolusi 1080p.
- [ ] Tidak ada notifikasi desktop masuk.
- [ ] Kursor tidak bergerak tanpa tujuan.
- [ ] Foto kendaraan tidak pecah.
- [ ] Overlay tidak menutupi tombol penting.

### Audio

- [ ] Voice-over tidak clipping.
- [ ] Noise sudah dibersihkan.
- [ ] Musik berada jauh di bawah suara narator.
- [ ] Tidak ada jeda kosong yang terlalu panjang.
- [ ] Pengucapan role dan status konsisten.

### Keamanan

- [ ] Token Fonnte tidak terlihat.
- [ ] Tidak ada data customer asli.
- [ ] Tidak ada password produksi.
- [ ] Nomor telepon yang tampil adalah data demo.
- [ ] Tab dan aplikasi lain sudah dipotong dari rekaman.

### Export

- [ ] Resolusi 1920 × 1080.
- [ ] Frame rate 30 fps.
- [ ] Codec H.264.
- [ ] Audio AAC minimal 192 kbps.
- [ ] Video ditonton ulang dari awal sampai akhir.
- [ ] File diuji pada laptop dan ponsel.

## 12. Flow presentasi setelah video

Setelah video selesai diputar, jangan langsung masuk ke penjelasan teknis. Gunakan tiga pertanyaan berikut untuk membuka diskusi:

1. Bagian operasional mana yang saat ini paling sering mengalami keterlambatan atau kehilangan informasi?
2. Approval mana yang paling penting untuk segera menerima notifikasi WhatsApp?
3. Laporan atau KPI tambahan apa yang dibutuhkan management setiap minggu?

Kemudian tawarkan demo langsung hanya pada modul yang paling relevan bagi client. Video menunjukkan keseluruhan sistem, sedangkan live demo digunakan untuk menjawab kebutuhan spesifik mereka.
