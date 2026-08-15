# **PRD LB AUTO**

# **ALUR KERJA :** 

**1 ALUR PEMBELIAN UNIT**

* INFO DARI LUAR  
  * Informasi unit mobil masuk dari berbagai sumber (Bursa, show room, perorangan, lelang, dll)  
* PIC PEMBELIAN (BP. KRISNA)  
  * Menawarkan unit mobil & harga  
* TAWAR MENAWAR  
  * Proses nego harga antara penjual & PIC Pembelian  
* CEK UNIT KE PIC (BP. CIPRUT)  
  * Pengecekan awal unit oleh PIC Ciprut  
* DELEGASIKAN TEAM CHECKER  
  * PIC Ciprut mendelegasikan ke team checker  
* CHECKER LAPANGAN (SESUAI AREA)  
  * Team checker mengecek unit sesuai area/ lokasi masing-masing  
* TEAM CHECKER MELAKUKAN PENGECEKAN  
  * KELAYAKAN BODY  
  * DOKUMEN LENGKAP (STNK, BPKB, PAJAK, DAN SURAT LAINNYA)  
* REPORT KE PIC  
  * Team checker melaporkan hasil pemeriksaan kepada PIC  
* KEPUTUSAN AKHIR (BP. KRISNA)  
  * PIC penentu mengambil keputusan unit diambil atau tidak  
* UNIT LAYAK & BISA DIJUAL  
  * PIC Penentu (Bp. Krisna) memutuskan untuk membeli unit (DEAL)  
* PEMBAYARAN  
  * Pembayaran unit mobil kepada penjual  
* UNIT TIDAK LAYAK  
  * Unit tidak diambil, proses selesai

**2 ALUR REPAIR & PERSIAPAN UNIT**

* SERAH TERIMA KE PIC REPAIR  
  * Unit diserahkan ke PIC Repair  
* PEMBAGIAN JENIS REPAIR  
  * PIC Repair membagi jenis pekerjaan sesuai kebutuhan unit  
* JENIS PEKERJAAN REPAIR BODY  
  * CAT BODY: Pengecatan ulang body  
  * PERBAIKAN PER PANEL: Pintu, kap mesin, dan seputarnya  
  * PENGGANTIAN TOTAL PANEL: Ganti total panel rusak parah  
  * PELURUSAN RANGKA: Perbaikan struktur atau sasis  
  * BUMPER REPAIR: Perbaikan bumper yang retak, renggang atau baret parah  
* PENGECATAN DALAM BODY REPAIR  
  * Aplikasi cat dasar, epoxy, top coat & clear coat  
* CEK DOKUMEN & KELENGKAPAN  
  * STNK (hidup/mati)  
  * BPKB  
  * Faktur  
  * Pajak  
  * Kelengkapan lain (buku buku, kunci, baut-baut, dll)

**3 ALUR PENJUALAN UNIT**

* FOTO & VIDEO UNIT (PIC BP. FEBI)  
  * Foto & video unit untuk keperluan jualan & medsos  
* EDIT & TAYANG IKLAN  
  * Hasil edit tayang di:  
    * OLX  
    * MOBIL123  
    * Media sosial lainnya  
* CUSTOMER DATANG  
  * Datang langsung ke showroom  
  * Melihat dari iklan  
* HANDLE OLEH TEAM SALES/MARKETING  
  * Proses penawaran & tawar menawar (Cash/Kredit)  
* JIKA KREDIT  
  * Hitung TDP, simulasi angsuran & arahkan ke vendor finance rekanan  
* TENTUKAN TENOR  
  * Tentukan jangka waktu pembayaran (1-5 Tahun)  
* DEAL & KIRIM UNIT  
  * Deal tercapai, unit dikirim ke konsumen  
* FOTO/VIDEO GREETING  
  * Ambil foto/video greeting singkat untuk LB (tentative: tergantung kesediaan konsumen)

# **PERAN USER & HAK AKSES (RBAC)**

| Role / User | PIC | Func |
| ----- | ----- | ----- |
| **Super Admin / Owner** | Management / Owner | Akses penuh seluruh data, monitoring dashboard profit/loss, override status, kelola user & role. |
| **PIC Pembelian** | Bp. Krisna | Input lead unit baru, nego harga awal, persetujuan keputusan beli (DEAL/CANCEL), bayar ke penjual. |
| **PIC Inspection Leader** | Bp. Ciprut | Cek awal unit, pendelegasian tugas ke Team Checker area, review hasil inspeksi lapangan. |
| **Team Checker (Field)** | Team Lapangan (Per Area)  | Pengecekan unit langsung di lokasi (Body, Mesin, Dokumen), upload foto/video & checklist inspeksi. |
| **PIC Repair & Workshop** | PIC Workshop | Menerima unit, alokasi pekerjaan repair (Body, Paint, Frame, Bumper), update progres & kelengkapan dokumen. |
| **PIC Marketing & Sales** | Bp. Febi & Team Sales  | Upload media (Foto/Video HD), posting ke OLX/Mobil123/Medsos, kelola lead customer, pengajuan kredit/cash, pengiriman unit.  |

# 

# **ALUR PENGGUNAAN APLIKASI**

1. **ACQUISITION**

1.1 Input Info Unit & Tawar Menawar  
Aktor: PIC Pembelian (Bp. Krisna)  
Input Data: Sumber unit (Bursa, Showroom, Perorangan, Lelang), Merk, Tipe, Tahun, Warna, Plat Nomor, Harga  
Penawaran Penjual, Kontak Penjual, Lokasi Mobil.  
Aksi System: Generate Unique ID Unit (misal: LBA-2026-0089). Status otomatis set ke SOURCED &  
NEGOTIATING.

1.2 Cek Unit Awal & Pendelegasian  
Aktor: PIC Inspection (Bp. Ciprut)  
Aksi System: Notifikasi push ke Bp. Ciprut saat ada unit baru. Bp. Ciprut melakukan peninjauan awal, lalu memilih  
nama Team Checker lapangan berdasarkan area lokasi mobil.  
Status Update: CHECKER\_ASSIGNED. Field Checker menerima task di mobile app.

1.3 Inspeksi Lapangan (Field Checker Execution)  
Aktor: Team Checker Lapangan  
Form Checklist Mobile:  
Kelayakan Body: Kondisi cat, bekas tabrakan/banjir, struktur sasis, kelurusan rangka, kondisi panel. (Upload foto  
bukti min. 6 sisi).  
Kelengkapan Dokumen: Status STNK (Hidup/Mati & Tgl Pajak), Keaslian BPKB, Faktur, Sertifikat NIK,  
Kesesuaian No. Rangka & No. Mesin.  
Kondisi Mesin & Interior: Suara mesin, kebocoran oli, fungsi AC, kelistrikan, odometer (KM).  
Output System: Skor kelayakan otomatis \+ Laporan Inspeksi PDF. Status update ke REPORT\_SUBMITTED.

1.4 Keputusan Akhir & Pembayaran  
Aktor: PIC Pembelian (Bp. Krisna)  
Logic Keputusan:  
UNIT LAYAK & BISA DIJUAL: Bp. Krisna klik tombol "DEAL BUY". Input Harga Beli Final & Tanggal Pembayaran.  
Sistem update status ke PURCHASED\_PAID. Form voucher pembayaran ter-generate.  
UNIT TIDAK LAYAK: Bp. Krisna klik tombol "REJECT". Input alasan penolakan. Status berubah ke REJECTED  
(Proses Selesai/Archive).

2. **REPAIR**

**2.1 Serah Terima & Alokasi Pekerjaan Repair**  
Aktor: PIC Repair / Workshop Manager  
Aksi System: Menerima notifikasi unit baru berstatus. PIC Repair melakukan konfirmasi penerimaan fisik unit (Serah Terima)   
Pembagian Jenis Repair (Multi-Select Checklist & Estimation Cost):

| Kategori Repair | Deskripsi Pekerjaan | Estimasi Biaya & Sub-Vendor |
| :---- | :---- | :---- |
| Cat Body | Pengecatan ulang full body / siram. | Rp \[Input\] | Internal / Vendor X |
| Perbaikan Per Panel | Perbaikan spesifik: Pintu, Kap Mesin, Bagasi, Fender, Roof. | Rp \[Input\] | Detail Panel Checklist |
| Penggantian Total Panel | Ganti panel total akibat rusak parah / tidak bisa dikenteng. | Rp \[Input\] | Part Order Logging |
| Pelurusan Rangka | Perbaikan struktur utama, sasis, atau rack steer. | Rp \[Input\] | Specialized Bench Work |
| Bumper Repair | Repair bumper retak, renggang, atau baret parah. | Rp \[Input\] | Plastic Welding & Fitting |

**2.2 Pengecatan & Stage Tracking (Body Repair Lifecycle)**  
Untuk pekerjaan cat, sistem menyediakan sub-stage tracking guna memantau progres bengkel:  
Stage 1: Cat Dasar & Putty (Dempul)  
Stage 2: Epoxy Primer Application  
Stage 3: Top Coat (Warna Utama)  
Stage 4: Clear Coat & Polishing (Vernis & Salon)

**2.3 Cek Dokumen & Kelengkapan Fisik**  
Aktor: Admin Document & PIC Repair  
Checklist Vault Digital (Must-Check before Sale):  
\[ \] STNK: Status (Hidup / Mati) | Tgl Jatuh Tempo Pajak | Tgl STNK.  
\[ \] BPKB: Ada / Proses BBN / Agunan.  
\[ \] Faktur & Sertifikat: Lembar Faktur Asli & NIK.  
\[ \] Kwitansi Kosong & Fotokopi KTP Pemilik Asli.  
\[ \] Kelengkapan Fisik Unit: Buku Servis, Buku Manual, Kunci Cadangan (Serep), Jack/Dongkrak, Tool Kit, Baut  
Roda.  
Output System: Menghitung Total HPP Unit \= (Harga Beli Unit \+ Total Realisasi Biaya Repair). Jika semua checklist  
OK \-\> berubah status sukses.

3. **SELLING**

**3.1 Foto/Video Unit & Media Studio (Bp. Febi)**  
Aktor: PIC Media & Marketing (Bp. Febi)  
Aksi System: Upload media HD ke sistem (Eksterior 360°, Interior, Mesin, Sound Engine, Video Walkaround).  
Status Update: Sistem otomatis meng-generate watermarked photo LB AUTO.

**3.2 Edit & Tayang Iklan Multi-Channel**  
Aktor: Team Marketing  
Integrasi Channel: Checklist publikasi ke OLX, Mobil123, Instagram / TikTok / Facebook Marketplace.  
Fitur Deskripsi Otomatis: Generator teks iklan berbasis template (Merk, Tahun, KM, Kondisi Pajak, Paket DP  
Murah). Status: PUBLISHED.

**3.3 Penanganan Prospect Customer & Negosiasi Sales**  
Aktor: Team Sales / Marketing  
Sumber Lead: Datang langsung ke Showroom / Inbound dari Iklan Online.  
Pilihan skema pembayaran:  
SKEMA CASH: Input Harga Kesepakatan \-\> Cetak SPK (Surat Pemesanan Kendaraan).  
SKEMA KREDIT: Lanjut ke modul kalkulator simulasi kredit.

**3.4 Simulasi Kredit & Approval Finance Rekanan**  
Aktor: Team Sales & Finance Admin  
Kalkulator Kredit Built-in:  
Input Harga OTR Deal, Total DP (TDP), Angsuran per Bulan.  
Pilihan Tenor: 1 Tahun (12x), 2 Tahun (24x), 3 Tahun (36x), 4 Tahun (48x), 5 Tahun (60x).  
Pilihan Leasing Rekanan: (BCA Finance, Adira, Otto, Mandiri Utama Finance, dll).  
Status Processing: SURVEY\_FINANCE \-\> FINANCE\_APPROVED.

**3.5 Deal, Pelunasan, Delivery & Greeting Media**  
Aktor: Team Sales & Customer  
Penyerahan Unit: Verifikasi pelunasan (Cash / Pencairan Leasing) \-\> Cetak Kwitansi & Bastk (Berita Acara Serah  
Terima Kendaraan).  
Foto/Video Greeting (Tentative): Capture momen penyerahan unit ke konsumen (jika konsumen bersedia). Direct  
upload ke gallery aplikasi & medsos.  
Status Akhir: SOLD\_DELIVERED. Selesai.

# 

# **FITUR**

1. **Mobile App Input (Field Checker & Repair Team)**  
     
* Simple Dashboard: List Tugas Inspeksi & List Unit dalam Bengkel.  
* Camera Direct Capture: Langsung foto komponen fisik (tidak bisa ambil dari gallery untuk cegah kecurangan).  
* Offline-First Mode: Bekerja di area susah sinyal, sync saat online.  
* Quick Checklist Tap: Interface tombol besar (Pass / Fail / Need Repair).

2. **Dashboard Monitoring (Management & Sales)**  
     
* Kanban Board Status Mobil: Drag and drop unit dari SOURCED \-\> REPAIR \-\> PUBLISHED \-\> SOLD.  
* HPP & Profit Margin Calculator: Otomatis hitung laba rugi per unit.  
* Leasing Simulator Widget: Hitung simulasi TDP & angsuran dalam hitungan detik di depan customer.  
* Export PDF & Excel: Cetak SPK, Kwitansi, & Laporan Penjualan.  
    
3. **Push Notifications**  
     
* Notif ke Bp. Ciprut saat Bp. Krisna memasukkan lead unit baru.  
* Notif ke Bp. Krisna saat Team Checker selesai upload Laporan Inspeksi.  
* Notif ke Bp. Febi saat Unit selesai repair & lolos Document QC.  
* Push Notification App: Alerts untuk deadline perbaikan unit & pembayaran pajak STNK yang hampir jatuh tempo.

# **DETAIL PAGES**

**P-01 Halaman Login & Autentikasi User**

* Form Input Username/Email & Password dengan Toggle Show/Hide Password.  
* Logo LB AUTO & Status Indikator Koneksi Server.

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| username | Text | wajib | Username pengguna |
| pass\_user | Password input | wajib | Kata sandi |

**P-02 Dashboard Utama / Executive Management Dashboard**

* Widget Metric Card: Total Unit Aktif, Unit Selesai Repair, Unit Published, Total Penjualan Bulan Ini, Profit Running.  
* Chart & Grafik Interactive: Trend Penjualan Cash vs Kredit & Turnover Rate Unit (Dwell Time Stok).  
* Alert Bar: Peringatan Pajak STNK Jatuh Tempo (H-30) & Deadline Perbaikan Bengkel Overdue.

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| filter\_periode\_dashboard | Date Range Picker | wajib | Filter grafik |
| filter\_cabang\_showroom | Dropdown Select | wajib | Filter Lokasi showroom |

**P-03 Modul Kalender Operasional Terpadu / Master Operational**  
**Calendar**

* Mode Tampilan: Monthly View, Weekly View, Daily Timeline, & Agenda List View.  
* Color-Coded Events: Biru (Inspeksi), Kuning (Repair Bengkel), Merah (Jatuh Tempo Pajak), Hijau (Test Drive/Delivery).  
* Interactive Modal Event: Klik event untuk edit detail & auto-sync ke WhatsApp Reminder.

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| judul\_agenda\_event | Text Input | wajib | Nama aktivitas/agenda operasional. |
| jenis\_event\_kalender | Dropdown Select | wajib | \[Inspeksi Lapangan, Target Repair, Jatuh Tempo Pajak, Test Drive/Delivery\] |
| tanggal\_jam\_event | DateTime Picker | wajib | Waktu pelaksanaan agenda. |
| car\_id\_referensi | Autocomplete Select | wajib | Mobil yang terkait dengan agenda tersebut. |
| pic\_assigned\_event | Dropdown Select | wajib | Petugas yang bertanggung jawab atas agenda. |
| catatan\_agenda | Long Text Area | Opsional | Instruksi atau catatan detail jadwal. |

**P-04 Halaman Lead Sourcing & Input Unit Baru** 

* Form Input Terstruktur Modul 1 (Informasi Penjual, Spesifikasi Mobil, & Harga Penawaran).   
* Button "Submit Prospek & Minta Cek Awal (Assign ke Bp. Ciprut)". 

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| sumber\_unit | Dropdown Select | Wajib | \[Bursa Mobil, Showroom Mitra, Perorangan, Lelang, Agent/Broker\] |
| nama\_penjual\_pemberi\_info | Text Input | Wajib | Nama lengkap pemilik / broker sumber. |
| no\_telp\_penjual | Phone Input | Wajib | Nomor telepon/WA aktif penjual (+62). |
| merek\_kendaraan | Dropdown / Autocomplete | Wajib | Toyota, Honda, Mitsubishi, Suzuki, Daihatsu, dll. |
| tipe\_varian | Text Input | Wajib | Contoh: Avanza 1.5 G CVT, Brio RS 1.2 AT. |
| tahun\_pembuatan | Number / Year Picker | Wajib | Tahun perakitan kendaraan. |
| transmisi | Radio Button | Wajib | \[Manual (MT), Otomatis (AT/CVT)\] |
| warna\_eksterior | Text Input | Wajib | Warna kendaraan sesuai STNK. |
| nomor\_polisi | Text Input (Uppercase) | Wajib | Nomor Plat Kendaraan (misal: B 1234 ABC). |
| nomor\_rangka\_vin | Text Input | Wajib | 17 digit nomor sasis/VIN. |
| nomor\_mesin | Text Input | Wajib | Nomor blok mesin kendaraan. |
| odometer\_km | Numeric Input | Wajib | Jumlah jarak tempuh kendaraan (KM). |
| lokasi\_keberadaan\_unit | Text Input | Wajib | Alamat/Kota lokasi mobil berada. |
| harga\_penawaran\_penjual | Currency Input (IDR) | Wajib | Harga penawaran awal dari pihak penjual. |
| target\_harga\_nego | Currency Input (IDR) | Opsional | Batas harga beli maksimal Bp. Krisna. |

**P-05 Halaman Field Inspection**

* Checklist Stepper Mobile: Step 1 Body Work ➔ Step 2 Mesin & Kaki-kaki ➔ Step 3 Dokumen.  
* Direct Camera Viewport: Pengambilan foto fisik langsung via kamera HP (mencegah manipulasi dari galeri).  
* Digital Signature Pad: Tanda tangan digital checker di layar HP.

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| skor\_kelayakan\_body | Slider / Rating (1-100) | Wajib | Nilai skor kondisi fisik & kelurusan rangka. |
| status\_bekas\_tabrak\_besar | Toggle Switch (Yes/No) | Wajib | Indikasi tulang sasis/apron/pillar bekas terbentur. |
| status\_bekas\_banjir | Toggle Switch (Yes/No) | Wajib | Indikasi karat/lumpur di kolong dashboard & ECU. |
| foto\_inspeksi\_fisik | Direct Camera Capture | Wajib | Min. 8 Foto wajib (Depan, Belakang, Kanan, Kiri, Mesin, Interior, Sasis, Odometer). |
| kondisi\_mesin\_suara | Radio Button | Wajib | \[Halus/Normal, Kasar/Berisik, Pincang/Getar\] |
| kondisi\_kebocoran\_oli | Radio Button | Wajib | \[Kering, Rembes Tipis, Bocor Parah\] |
| kondisi\_kaki\_kaki\_suspensi | Radio Button | Wajib | \[Senyap/Normal, Bunyi Gluduk, Rusak Parah\] |
| status\_pajak\_stnk | Radio Button | Wajib | \[Pajak Hidup, Pajak Mati (Isi tgl mati)\] |
| catatan\_khusus\_checker | Long Text Area | Opsional | Catatan tambahan kekurangan atau rekomendasi. |

**P-06 Halaman Review & Approval Pembelian / Purchase Decision**

* PDF Inspector Report Live Previewer & Visual Body Score Summary.  
* Modal Action Button: "DEAL BUY" vs "REJECT / BATAL".  
* Form Generate Voucher Pembayaran ke Penjual.

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| keputusan\_pembelian | Radio Button | Wajib | \[DEAL (Beli), REJECT (Batal Beli)\] |
| alasan\_penolakan | Text Input | Conditional | Wajib diisi jika keputusan \= REJECT. |
| harga\_deal\_pembelian | Currency Input (IDR) | Conditional | Harga kesepakatan akhir pembelian unit jika DEAL. |
| metode\_pembayaran\_pembelian | Dropdown Select | Conditional | \[Transfer Bank, Cash, DP \+ Pelunasan\] |
| bukti\_transfer\_pembayaran | File Upload (PDF/JPG) | Conditional | Upload bukti bayar resmi LB AUTO ke penjual. |

**P-07 Halaman Master Data Stok Fleet / Fleet Inventory List**

* Datatable Interaktif dengan Sorting, Pagination, dan Custom Column View.  
* Multi-Filter Bar: Plat Nomor, Tahun, Status Operasional, Range HPP.  
* Button Export Data (Excel/PDF) & Fast Action Modal Buttons.

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| search\_query\_table | Text Input | Opsional | Pencarian bebas berdasarkan kata kunci Nopol, Merk, atau VIN. |
| filter\_status\_armada | Multi-Select Dropdown | Opsional | Filter berdasarkan status tertentu (misal: IN\_REPAIR, PUBLISHED). |

**P-08 Halaman Detail Unit Mobil Master  (Opsional)**

* Tab Overview: Spesifikasi Mobil, Lokasi Unit, Status Terkini.  
* Tab Inspection Log: Hasil Pemeriksaan Field Checker & Galeri Kerusakan.  
* Tab Cost & HPP Log: Rincian Biaya Beli \+ Realisasi Repair \= Total HPP Unit.  
* Tab Document Vault: Status STNK, BPKB, Faktur, & Aksesoris Fisik.  
* Tab Marketing & Media: Galeri Foto HD & Link Active Posting Marketplaces.

**P-09 Halaman Workshop Work Order & Repair Allocation**

* Multi-Select Checklist Jenis Pekerjaan Repair & Checklist Panel Spesifik.  
* Tracker Sub-Stage Pengecatan (Stage 1 Dempul ➔ Stage 2 Epoxy ➔ Stage 3 Top Coat ➔ Stage 4 Clear Coat).  
* Form Pencatatan Biaya Estimasi vs Realisasi Final.

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| kategori\_repair\_dipilih | Multi-Select Checkbox | Wajib | \[Cat Body, Perbaikan Per Panel, Penggantian Total Panel, Pelurusan Rangka, Bumper Repair\] |
| detail\_panel\_diperbaiki | Checklist Grid Panel | Opsional | Checklist spesifik (Pintu, Kap Mesin, Fender, Roof, Bumper). |
| sub\_stage\_pengecatan | Progress Dropdown | Wajib | \[Stage 1: Cat Dasar/Dempul, Stage 2: Epoxy Primer, Stage 3: Top Coat Warna, Stage 4: Clear Coat & Salon\] |
| nama\_vendor\_bengkel\_mitra | Text / Select Vendor | Wajib | Nama bengkel internal atau bengkel rekanan luar. |
| estimasi\_biaya\_repair | Currency Input (IDR) | Wajib | Estimasi awal total biaya perbaikan. |
| realisasi\_biaya\_repair\_final | Currency Input (IDR) | Wajib | Biaya aktual yang dibayar setelah pekerjaan selesai. |
| foto\_sebelum\_dan\_sesudah\_repair | Multi-File Upload | Wajib | Foto komparasi fisik Before & After pengerjaan. |

**P-10 Halaman Digital Document Vault & Legal Compliance**

* Checklist Vault Status Dokumen & Date Picker Jatuh Tempo Pajak.  
* Viewer Lampiran Foto Dokumen Berkas Legalitas.  
* Status Badge Indicator: "DOKUMEN LENGKAP & READY JUAL".

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| keberadaan\_stnk\_asli | Radio Button | Wajib | \[Ada Asli, Duplikat, Hilang/Proses\] |
| tanggal\_jatuh\_tempo\_pajak\_stnk | Date Picker | Wajib | Tanggal mati pajak tahunan (auto-alert H-30). |
| tanggal\_jatuh\_tempo\_plat\_5thn | Date Picker | Wajib | Tanggal kadaluarsa Plat Nomor 5 Tahunan. |
| keberadaan\_bpkb\_asli | Radio Button | Wajib | \[Ada Asli, Sekolah/Agunan Leasing, Proses BBN\] |
| nomor\_bpkb | Text Input | Wajib | Nomor unik buku BPKB. |
| keberadaan\_faktur\_sertifikat\_nik | Radio Button | Wajib | \[Lengkap Ada, Tidak Ada\] |
| kwitansi\_kosong\_ktp\_pemilik | Checkbox Checklist | Wajib | \[ \] Kwitansi Beli Bermaterai, \[ \] FC KTP Pemilik Pertama. |
| kelengkapan\_aksesoris\_fisik | Multi-Select Checklist | Wajib | \[ \] Kunci Cadangan (Serep), \[ \] Buku Servis, \[ \] Buku Manual, \[ \] Dongkrak/Tool Kit, \[ \] Baut Roda Cadangan. |

**P-11 Halaman Media Studio Upload & Listing Publisher**

* Drag-and-Drop Multi Photo Upload Studio & Auto-Watermark Tool.  
* Auto-Generated Description Text Generator (berbasis template spesifikasi mobil).  
* Checklist Publisher Channel (OLX, Mobil123, Instagram, TikTok, FB Marketplace).

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| galeri\_foto\_hd\_studio | Multi-File Upload | Wajib | Min 10 foto kualitas HD eksterior, interior & mesin. |
| link\_video\_walkaround\_youtube\_tiktok | URL Input | Opsional | Link video review unit di YouTube Shorts / TikTok. |
| target\_harga\_jual\_cash | Currency Input (IDR) | Wajib | Harga penawaran jualan tunai/cash di iklan. |
| target\_harga\_jual\_kredit | Currency Input (IDR) | Wajib | Harga promo OTR khusus pembelian paket kredit. |
| deskripsi\_iklan\_custom | Rich Text Editor | Wajib | Teks promosi jualan yang akan ditayangkan. |
| channel\_publikasi\_aktif | Multi-Select Checklist | Wajib | \[ \] OLX Indonesia, \[ \] Mobil123, \[ \] Instagram Feed/Story, \[ \] TikTok Shop, \[ \] FB Marketplace. |

**P-12 Halaman Customer CRM & Lead Management**

* Datatable Prospect Lead Customer & Lead Status Stepper (New Lead ➔ Follow Up ➔ Scheduled Test Drive ➔ SPK Issued ➔ Closed / Lost).  
* Direct WhatsApp Chat Action Button.

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| nama\_calon\_pembeli | Text Input | Wajib | Nama panggilan/lengkap prospect. |
| no\_wa\_pembeli | Phone Input | Wajib | Nomor WhatsApp calon pembeli. |
| sumber\_lead\_iklan | Dropdown Select | Wajib | \[OLX, Mobil123, Instagram, TikTok, Walk-in Showroom\] |
| catatan\_follow\_up | Long Text Area | Opsional | Catatan interaksi & janji temu test drive. |

**P-13 Halaman HPP & Simulator Kalkulator Kredit Leasing**

* Interactive Range Sliders: Slider Harga OTR Deal & Slider Total DP (TDP).  
* Radio Button Tenor Kredit (12, 24, 36, 48, 60 Bulan).  
* Dropdown Vendor Leasing Rekanan & Hasil Kalkulasi Real-time.

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| harga\_otr\_deal | Currency Input / Slider | Wajib | Harga OTR kesepakatan jualan. |
| nilai\_total\_dp\_tdp | Currency Input / Slider | Conditional | Total Uang Muka (DP Murni \+ Admin \+ Asuransi). |
| pilihan\_tenor\_kredit | Radio Button / Dropdown | Conditional | \[1 Tahun (12x), 2 Tahun (24x), 3 Tahun (36x), 4 Tahun (48x), 5 Tahun (60x)\] |
| vendor\_leasing\_rekanan | Dropdown Select | Conditional | \[BCA Finance, Adira Finance, Oto Multiartha, Mandiri Utama Finance, dll\] |
| nilai\_angsuran\_per\_bulan | Currency Output (Read-only) | Computed | Nominal cicilan per bulan hasil simulasi. |

**P-14 Halaman Generator SPK & Kwitansi Pelunasan**

* Form Input Data KTP Pembeli & Summary Transaksi Penjualan.  
* PDF Instant Generator: Button "Cetak SPK", "Cetak Kwitansi", & "Cetak BASTK" dilengkapi QR Code Validasi.

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| nama\_lengkap\_pembeli | Text Input | Wajib | Nama resmi pembeli sesuai KTP. |
| nomor\_nik\_ktp\_pembeli | Numeric Input (16 Digit) | Wajib | Nomor Induk Kependudukan (NIK) KTP. |
| nomor\_whatsapp\_pembeli | Phone Input | Wajib | Nomor WA aktif untuk pengiriman PDF SPK/ Kwitansi. |
| alamat\_domisili\_pembeli | Long Text Area | Wajib | Alamat pengiriman unit & BASTK. |
| skema\_pembayaran\_dipilih | Radio Button | Wajib | \[CASH, KREDIT\] |
| harga\_jual\_deal\_akhir | Currency Input (IDR) | Wajib | Harga akhir kesepakatan transaksi penjualan. |

**P-15 Halaman Delivery & Greeting Media Gallery**

* Upload Photo/Video Greeting Area & Rating Kepuasan Bintang (1–5).  
* Auto-Share Button ke Story Instagram / Facebook Page LB AUTO.

| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| foto\_video\_greeting\_delivery | File / Media Capture | Opsional | Foto/video serah terima unit (jika konsumen bersedia). |
| rating\_kepuasan\_konsumen | Star Rating (1-5) | Opsional | Tingkat kepuasan layanan pembeli. |

**P-16 Halaman Laporan keuangan & Profit Loss Analisis**

* Tabel Analisis Profit/Loss Per Unit (Harga Jual \- Total HPP \= Net Profit).  
* Chart Grafik Omzet Bulanan & Biaya Bengkel Kumulatif.  
* Button Export Laporan Financial Format Excel (.xlsx).

Halaman analitik read-only dengan kontrol filter periode tanggal & export file report.

**P-17 Halaman Pengaturan Sistem, User Management & System Log**

* Datatable User Account (Add, Edit, Deactivate User).  
* RBAC Matrix Toggles Permissions & Configuration Input Form (WhatsApp API Key).  
* System Activity Audit Trail Table.


| Variable Field | Tipe Control | Status | Desc |
| :---- | :---- | :---- | :---- |
| nama\_lengkap\_user | Text Input | Wajib | Nama pengguna aplikasi. |
| email\_user | Email Input | Wajib | Email login pengguna. |
| role\_akses\_assigned | Dropdown Select | Wajib | \[ROLE\_OWNER, ROLE\_BUYER, ROLE\_INSPECTOR\_LEAD, ROLE\_FIELD\_CHECKER, ROLE\_REPAIR\_PIC, ROLE\_SALES\] |
| whatsapp\_gateway\_api\_key | Password / Text Input | Wajib Config | API Key token untuk pengiriman notifikasi otomatis WA. |

