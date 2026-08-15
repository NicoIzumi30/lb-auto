# Panduan Deployment LB AUTO dengan systemd dan Cloudflare Tunnel

Panduan ini menggunakan arsitektur berikut:

```text
Browser pengguna
       │
       │ HTTPS
       ▼
Cloudflare Access / WAF
       │
       │ Cloudflare Tunnel, koneksi keluar dari server
       ▼
cloudflared.service
       │
       │ HTTP lokal 127.0.0.1:8542
       ▼
lb-auto.service
       │
       ├── FastAPI + frontend PWA
       ├── SQLite: /opt/lb-auto/lb_auto.db
       └── Upload: /opt/lb-auto/uploads/
```

Port aplikasi tidak dibuka ke internet. `cloudflared` membangun koneksi outbound ke Cloudflare dan meneruskan hostname publik ke `127.0.0.1:8542`. Cloudflare menyatakan Tunnel bekerja menggunakan koneksi keluar sehingga origin tidak memerlukan port inbound publik. Lihat [Cloudflare Tunnel documentation](https://developers.cloudflare.com/tunnel/).

## 1. Keputusan deployment

Konfigurasi yang disarankan untuk aplikasi saat ini:

| Komponen | Pilihan |
| --- | --- |
| Sistem operasi | Ubuntu Server 22.04/24.04 atau Debian 12 |
| Lokasi aplikasi | `/opt/lb-auto` |
| User service | User Linux yang digunakan untuk deployment |
| Source code | Clone SSH dari `git@github.com:NicoIzumi30/lb-auto.git` |
| Python | Virtual environment di `/opt/lb-auto/.venv` |
| App server | Uvicorn melalui `lb-auto.service` |
| Bind address | `127.0.0.1:8542` |
| Worker | Tepat 1 worker selama menggunakan SQLite |
| Public ingress | Cloudflare Tunnel |
| Tunnel management | Remotely managed dari dashboard Cloudflare |
| Proteksi tambahan | Cloudflare Access untuk user internal |
| Backup | SQLite online backup + folder uploads setiap hari |

Nginx tidak wajib untuk arsitektur ini karena `cloudflared` dapat langsung meneruskan request HTTP ke Uvicorn lokal.

## 2. Prasyarat

Siapkan:

1. Server atau VM Linux yang selalu menyala.
2. Akses `sudo` ke server.
3. Akun GitHub yang mempunyai akses ke repository LB AUTO.
4. SSH key GitHub pada user Linux yang menjalankan deployment.
5. Domain aktif di akun Cloudflare.
6. Subdomain, misalnya `app.lbauto.co.id`.
7. Akses ke Cloudflare Zero Trust/Networking.
8. Token Fonnte produksi yang baru.
9. Backup database dan uploads sebelum migrasi atau update.

Cloudflare mencantumkan akun, domain di Cloudflare, serta server dengan akses internet sebagai prasyarat untuk published application. Lihat [official Tunnel setup](https://developers.cloudflare.com/tunnel/setup/).

## 3. Catatan keamanan sebelum mulai

Wajib dilakukan sebelum hostname dipublikasikan:

1. Ganti `LB_AUTO_SECRET` dengan nilai acak.
2. Rotasi token Fonnte yang sebelumnya pernah dibagikan melalui percakapan atau media lain.
3. Jangan menyalin file `.env` development ke server produksi.
4. Ganti password seluruh akun bawaan sebelum aplikasi digunakan.
5. Aktifkan Cloudflare Access jika aplikasi hanya digunakan staf LB AUTO.
6. Jangan membuka port 8542 pada firewall/router.
7. Jangan menjalankan Uvicorn sebagai `root`.
8. Gunakan satu Uvicorn worker karena penyimpanan masih SQLite.

## 4. Menyiapkan server Linux

Update paket dan instal kebutuhan dasar:

```bash
sudo apt update
sudo apt install -y git openssh-client python3 python3-venv python3-pip sqlite3 rsync curl ca-certificates
```

Periksa user Linux yang akan menjalankan aplikasi:

```bash
id
whoami
```

User tersebut harus mempunyai akses `sudo` dan SSH key yang terhubung ke akun GitHub.

Jika SSH key belum tersedia, buat key sebagai user tersebut:

```bash
ssh-keygen -t ed25519 -C "server-lb-auto"
```

Tampilkan public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

Tambahkan public key ke **GitHub → Settings → SSH and GPG keys**, lalu uji koneksi:

```bash
ssh -T git@github.com
```

GitHub dapat meminta konfirmasi fingerprint saat koneksi pertama. Pastikan fingerprint sesuai dokumentasi GitHub sebelum menjawab `yes`.

## 5. Clone source code dari GitHub

Buat direktori aplikasi dengan kepemilikan user Linux yang sedang digunakan:

```bash
sudo install -d -o "$(id -un)" -g "$(id -gn)" -m 0750 /opt/lb-auto
```

Clone repository melalui SSH:

```bash
git clone git@github.com:NicoIzumi30/lb-auto.git /opt/lb-auto
```

Periksa branch dan remote:

```bash
cd /opt/lb-auto
git remote -v
git branch --show-current
```

Pastikan file berikut tersedia:

```bash
ls -la /opt/lb-auto
```

Minimal harus ada `backend`, `assets`, `app.js`, `index.html`, `styles.css`, dan `requirements.txt`.

## 6. Membuat Python virtual environment

Buat virtual environment menggunakan user Linux deployment:

```bash
cd /opt/lb-auto
python3 -m venv .venv
```

Instal dependensi:

```bash
/opt/lb-auto/.venv/bin/pip install --upgrade pip
/opt/lb-auto/.venv/bin/pip install -r /opt/lb-auto/requirements.txt
```

Verifikasi:

```bash
/opt/lb-auto/.venv/bin/python -c "import fastapi, uvicorn; print('dependencies ok')"
```

## 7. Membuat environment produksi

Buat direktori konfigurasi di luar source code:

```bash
sudo install -d -o root -g root -m 0750 /etc/lb-auto
```

Salin template:

```bash
sudo install -o root -g root -m 0600 \
  /opt/lb-auto/deploy/lb-auto.env.example \
  /etc/lb-auto/lb-auto.env
```

Hasilkan application secret:

```bash
openssl rand -hex 32
```

Salin hasilnya, lalu edit environment:

```bash
sudoedit /etc/lb-auto/lb-auto.env
```

Isi dengan nilai produksi:

```env
LB_AUTO_SECRET=PASTE_RANDOM_SECRET_DI_SINI
APP_BASE_URL=https://app.example.com
FONNTE_ENABLED=true
FONNTE_TOKEN=PASTE_TOKEN_FONNTE_BARU_DI_SINI
```

Ganti `app.example.com` dengan hostname sebenarnya.

Periksa permission tanpa menampilkan isi rahasia:

```bash
sudo stat -c '%a %U:%G %n' /etc/lb-auto/lb-auto.env
```

Hasil yang diharapkan:

```text
600 root:root /etc/lb-auto/lb-auto.env
```

Jangan memasukkan file environment ke Git atau menyalinnya ke dokumentasi.

## 8. Inisialisasi database dan akun aplikasi

Inisialisasi schema serta data awal:

```bash
cd /opt/lb-auto
/opt/lb-auto/.venv/bin/python -m backend.seed
```

Tampilkan akun yang tersedia:

```bash
/opt/lb-auto/.venv/bin/python -m backend.admin list-users
```

Gunakan akun yang sudah tersedia. Tidak perlu membuat user aplikasi baru. Ganti password masing-masing akun:

Jalankan untuk masing-masing akun:

```bash
/opt/lb-auto/.venv/bin/python -m backend.admin set-password owner@lbauto.id
/opt/lb-auto/.venv/bin/python -m backend.admin set-password krisna@lbauto.id
/opt/lb-auto/.venv/bin/python -m backend.admin set-password ciprut@lbauto.id
/opt/lb-auto/.venv/bin/python -m backend.admin set-password checker@lbauto.id
/opt/lb-auto/.venv/bin/python -m backend.admin set-password legal@lbauto.id
/opt/lb-auto/.venv/bin/python -m backend.admin set-password hod@lbauto.id
/opt/lb-auto/.venv/bin/python -m backend.admin set-password workshop@lbauto.id
/opt/lb-auto/.venv/bin/python -m backend.admin set-password sales@lbauto.id
```

CLI meminta password secara interaktif sehingga password tidak masuk ke shell history. Gunakan password unik minimal 12 karakter untuk setiap akun.

## 9. Memasang service FastAPI

Template telah tersedia di:

```text
/opt/lb-auto/deploy/lb-auto.service
```

Pasang unit file:

```bash
APP_USER="$(id -un)"
APP_GROUP="$(id -gn)"
sed \
  -e "s/__LB_AUTO_USER__/${APP_USER}/g" \
  -e "s/__LB_AUTO_GROUP__/${APP_GROUP}/g" \
  /opt/lb-auto/deploy/lb-auto.service | \
  sudo tee /etc/systemd/system/lb-auto.service >/dev/null
sudo chmod 0644 /etc/systemd/system/lb-auto.service
```

Perintah tersebut mengisi `User=` dan `Group=` memakai user Linux yang menjalankan deployment. Verifikasi hasilnya:

```bash
sudo systemctl cat lb-auto.service
```

Pastikan tidak ada teks `__LB_AUTO_USER__` atau `__LB_AUTO_GROUP__` yang tersisa.

Muat ulang systemd dan jalankan service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now lb-auto.service
```

Periksa status:

```bash
sudo systemctl status lb-auto.service --no-pager
```

Periksa log:

```bash
sudo journalctl -u lb-auto.service -n 100 --no-pager
```

Ikuti log secara real-time:

```bash
sudo journalctl -u lb-auto.service -f
```

Tes aplikasi dari server:

```bash
curl -s http://127.0.0.1:8542/api/health
```

Hasil yang diharapkan:

```json
{"status":"ok","service":"LB AUTO API"}
```

Pastikan Uvicorn hanya mendengarkan localhost:

```bash
sudo ss -ltnp | grep ':8542'
```

Alamat yang diharapkan adalah `127.0.0.1:8542`, bukan `0.0.0.0:8542`.

## 10. Menginstal cloudflared

Metode paling mudah adalah menggunakan perintah yang diberikan langsung oleh dashboard Cloudflare saat membuat Tunnel. Cloudflare juga menyediakan package repository resmi pada [pkg.cloudflare.com](https://pkg.cloudflare.com/).

Untuk Debian/Ubuntu, paket stable dapat dipasang dengan:

```bash
sudo mkdir -p --mode=0755 /usr/share/keyrings
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | \
  sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' | \
  sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt update
sudo apt install -y cloudflared
```

Periksa instalasi:

```bash
cloudflared --version
```

## 11. Membuat Cloudflare Tunnel

Gunakan remotely-managed tunnel agar hostname dan route dapat dikelola dari dashboard.

1. Login ke Cloudflare Dashboard.
2. Buka **Networking → Tunnels**.
3. Pilih **Create a tunnel**.
4. Pilih connector `cloudflared`.
5. Beri nama, misalnya `lb-auto-production`.
6. Pilih Linux dan arsitektur server.
7. Salin perintah instalasi yang diberikan dashboard.

Alur dashboard resmi dijelaskan pada [Create a tunnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/get-started/create-remote-tunnel/).

Perintahnya akan menyerupai:

```bash
sudo cloudflared service install YOUR_TUNNEL_TOKEN
```

Jangan menaruh Tunnel token di repository, screenshot, chat, atau dokumen. Siapa pun yang memiliki token remotely-managed tunnel dapat menjalankan connector untuk tunnel tersebut. Cloudflare menyediakan prosedur rotasi pada [Tunnel tokens](https://developers.cloudflare.com/tunnel/advanced/tunnel-tokens/).

Setelah instalasi, periksa service:

```bash
sudo systemctl enable cloudflared.service
sudo systemctl restart cloudflared.service
sudo systemctl status cloudflared.service --no-pager
```

Periksa log:

```bash
sudo journalctl -u cloudflared.service -n 100 --no-pager
```

Dashboard harus menunjukkan status tunnel `Healthy`.

## 12. Menambahkan public hostname

Di tunnel `lb-auto-production`:

1. Buka tab **Routes**.
2. Pilih **Add route**.
3. Pilih **Published application**.
4. Isi subdomain, misalnya `app`.
5. Pilih domain, misalnya `lbauto.co.id`.
6. Pada Service URL masukkan:

```text
http://127.0.0.1:8542
```

7. Simpan route.

Mapping hostname ke local service merupakan model resmi published application Cloudflare Tunnel. Lihat [Tunnel routing](https://developers.cloudflare.com/tunnel/routing/).

Jangan menggunakan `https://127.0.0.1:8542` karena Uvicorn pada konfigurasi ini menyediakan HTTP lokal. HTTPS dihentikan di edge Cloudflare.

Tes melalui browser:

```text
https://app.lbauto.co.id
```

Ganti domain sesuai konfigurasi Anda.

## 13. Mengaktifkan Cloudflare Access

Aplikasi menyimpan data penjual, customer, dokumen, biaya, dan foto. Karena itu Cloudflare Access sangat disarankan sebagai lapisan autentikasi sebelum login aplikasi.

1. Buka **Cloudflare Zero Trust**.
2. Buka **Access controls → Applications**.
3. Pilih **Create new application**.
4. Pilih **Self-hosted and private**.
5. Isi nama `LB AUTO Production`.
6. Isi hostname aplikasi.
7. Buat policy `Allow` hanya untuk:
   - email perusahaan;
   - domain email perusahaan;
   - group tertentu pada identity provider; atau
   - daftar email staf yang diizinkan.
8. Aktifkan MFA pada identity provider.
9. Atur session duration sesuai kebijakan, misalnya 8–12 jam.
10. Simpan dan uji dari mode incognito.

Cloudflare menjelaskan bahwa Access bertindak sebagai identity-aware proxy yang memeriksa policy sebelum request mencapai aplikasi. Lihat [Add web applications](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/) dan [Create an Access application](https://developers.cloudflare.com/learning-paths/clientless-access/access-application/create-access-app/).

Hasil akhirnya mempunyai dua lapis login:

1. Cloudflare Access untuk memastikan perangkat/user boleh mencapai aplikasi.
2. Login LB AUTO untuk menentukan role operasional dan audit trail.

## 14. Setting Cloudflare yang disarankan

### Cache

Untuk aplikasi operasional internal, buat Cache Rule `Bypass cache` pada hostname aplikasi, terutama untuk:

```text
/api/*
/uploads/*
```

Tujuannya agar respons API serta media operasional tidak disimpan sebagai cache publik di edge.

### WAF dan rate limiting

Tambahkan rate limit pada:

```text
/api/auth/login
```

Nilai awal yang wajar adalah sekitar 10 percobaan per menit per IP, lalu sesuaikan dengan pola penggunaan. Jangan terlalu ketat apabila seluruh kantor memakai satu public IP.

### TLS

- Paksa HTTPS pada hostname aplikasi.
- Aktifkan Always Use HTTPS.
- Aktifkan HSTS hanya setelah domain dan Access sudah diuji dengan benar.
- Tidak perlu sertifikat origin tambahan untuk koneksi HTTP localhost dari `cloudflared` ke Uvicorn.

### Upload

Backend membatasi setiap upload hingga 8 MB dan hanya menerima JPG, PNG, atau WebP. Pastikan tidak ada Cloudflare rule yang menetapkan batas lebih kecil.

## 15. Firewall server

Karena Tunnel menggunakan koneksi outbound, port 8542 tidak perlu dibuka. Cloudflare menyarankan positive security model dengan memblokir ingress dan hanya mengizinkan koneksi yang diperlukan. Tunnel menggunakan outbound port `7844` melalui UDP untuk QUIC atau TCP untuk HTTP/2. Lihat [Tunnel with firewall](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/tunnel-with-firewall/).

Contoh UFW, apabila SSH menggunakan port standar:

```bash
sudo ufw allow OpenSSH
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable
sudo ufw status verbose
```

Penting: izinkan port SSH yang benar sebelum mengaktifkan firewall agar tidak terkunci dari server.

Jangan menjalankan:

```bash
sudo ufw allow 8542
```

Jika server menerapkan egress firewall ketat, izinkan outbound TCP dan UDP port `7844` ke endpoint Cloudflare Tunnel. QUIC direkomendasikan, tetapi `cloudflared` dapat fallback ke HTTP/2 melalui TCP jika UDP diblokir.

## 16. Backup otomatis

Cloudflare Tunnel bukan sistem backup. Data yang wajib dicadangkan:

```text
/opt/lb-auto/lb_auto.db
/opt/lb-auto/uploads/
```

Template backup telah tersedia:

```text
/opt/lb-auto/deploy/backup-lb-auto.sh
/opt/lb-auto/deploy/lb-auto-backup.service
/opt/lb-auto/deploy/lb-auto-backup.timer
```

Buat direktori backup:

```bash
sudo install -d -o "$(id -un)" -g "$(id -gn)" -m 0750 /var/backups/lb-auto
```

Pasang service dan timer:

```bash
APP_USER="$(id -un)"
APP_GROUP="$(id -gn)"
sed \
  -e "s/__LB_AUTO_USER__/${APP_USER}/g" \
  -e "s/__LB_AUTO_GROUP__/${APP_GROUP}/g" \
  /opt/lb-auto/deploy/lb-auto-backup.service | \
  sudo tee /etc/systemd/system/lb-auto-backup.service >/dev/null
sudo install -o root -g root -m 0644 \
  /opt/lb-auto/deploy/lb-auto-backup.timer \
  /etc/systemd/system/lb-auto-backup.timer
sudo chmod 0644 /etc/systemd/system/lb-auto-backup.service
sudo systemctl daemon-reload
sudo systemctl enable --now lb-auto-backup.timer
```

Timer berjalan setiap hari sekitar pukul 02:30 dan mempertahankan backup lokal selama 30 hari.

Tes backup pertama:

```bash
sudo systemctl start lb-auto-backup.service
sudo systemctl status lb-auto-backup.service --no-pager
sudo ls -lh /var/backups/lb-auto
```

Periksa jadwal:

```bash
systemctl list-timers lb-auto-backup.timer
```

Salin backup secara berkala ke storage lain yang terenkripsi. Backup pada disk yang sama tidak melindungi dari kerusakan disk atau kehilangan server.

## 17. Prosedur restore

Lakukan restore hanya saat maintenance window.

Hentikan aplikasi:

```bash
sudo systemctl stop lb-auto.service
```

Simpan data saat ini agar masih dapat dipulihkan:

```bash
sudo mv /opt/lb-auto/lb_auto.db /opt/lb-auto/lb_auto.db.before-restore
sudo mv /opt/lb-auto/uploads /opt/lb-auto/uploads.before-restore
```

Pulihkan database:

```bash
sudo cp /var/backups/lb-auto/lb_auto-YYYYMMDD-HHMMSS.db /opt/lb-auto/lb_auto.db
```

Pulihkan uploads:

```bash
sudo tar -C /opt/lb-auto -xzf /var/backups/lb-auto/uploads-YYYYMMDD-HHMMSS.tar.gz
```

Atur permission dan mulai aplikasi:

```bash
sudo chown -R "$(id -un):$(id -gn)" /opt/lb-auto/lb_auto.db /opt/lb-auto/uploads
sudo systemctl start lb-auto.service
curl -s http://127.0.0.1:8542/api/health
```

Login dan periksa beberapa unit, foto, user, serta laporan sebelum menutup maintenance window.

## 18. Prosedur update aplikasi

### 18.1 Backup sebelum update

```bash
sudo systemctl start lb-auto-backup.service
sudo systemctl status lb-auto-backup.service --no-pager
```

### 18.2 Ambil versi terbaru dari GitHub

Periksa status repository lalu tarik commit terbaru:

```bash
sudo systemctl stop lb-auto.service
cd /opt/lb-auto
git status --short
git pull --ff-only
```

`git pull --ff-only` menghentikan update jika repository server mempunyai commit lokal yang belum ada di remote. Selesaikan perubahan lokal sebelum melanjutkan. Database, `.env`, virtual environment, dan folder `uploads` berada di `.gitignore` sehingga data runtime tetap dipertahankan.

### 18.3 Update dependency dan validasi

```bash
/opt/lb-auto/.venv/bin/pip install -r /opt/lb-auto/requirements.txt
cd /opt/lb-auto
/opt/lb-auto/.venv/bin/python -m py_compile backend/*.py
/opt/lb-auto/.venv/bin/python -m unittest -v
```

### 18.4 Jalankan versi baru

```bash
sudo systemctl start lb-auto.service
sudo systemctl status lb-auto.service --no-pager
curl -s http://127.0.0.1:8542/api/health
```

Tidak perlu me-restart `cloudflared` jika hostname dan port lokal tidak berubah.

## 19. Operasi systemctl sehari-hari

### FastAPI

```bash
sudo systemctl start lb-auto
sudo systemctl stop lb-auto
sudo systemctl restart lb-auto
sudo systemctl status lb-auto --no-pager
sudo journalctl -u lb-auto -f
```

### Cloudflare Tunnel

```bash
sudo systemctl start cloudflared
sudo systemctl stop cloudflared
sudo systemctl restart cloudflared
sudo systemctl status cloudflared --no-pager
sudo journalctl -u cloudflared -f
```

### Backup

```bash
sudo systemctl start lb-auto-backup
sudo systemctl status lb-auto-backup --no-pager
systemctl list-timers lb-auto-backup.timer
```

Urutan diagnosis yang disarankan:

1. `lb-auto.service` harus sehat.
2. `curl http://127.0.0.1:8542/api/health` harus berhasil.
3. `cloudflared.service` harus sehat.
4. Tunnel harus `Healthy` di dashboard.
5. Baru periksa Access, DNS, WAF, dan browser.

## 20. Troubleshooting

### Aplikasi lokal tidak hidup

```bash
sudo systemctl status lb-auto --no-pager
sudo journalctl -u lb-auto -n 200 --no-pager
```

Periksa:

- path `/opt/lb-auto` benar;
- `.venv/bin/uvicorn` tersedia;
- environment file tersedia;
- user pada `User=` di service dapat menulis database dan uploads;
- port 8542 belum dipakai proses lain.

### Tunnel menampilkan 502 Bad Gateway

Tes origin lokal:

```bash
curl -v http://127.0.0.1:8542/api/health
```

Pastikan Service URL route adalah:

```text
http://127.0.0.1:8542
```

Cloudflare menjelaskan bahwa 502 pada Tunnel biasanya berarti connector tersambung tetapi tidak dapat menjangkau origin, port salah, atau protokol HTTP/HTTPS tidak sesuai. Lihat [Tunnel troubleshooting](https://developers.cloudflare.com/tunnel/troubleshooting/).

### Tunnel berstatus Down atau Degraded

```bash
sudo systemctl status cloudflared --no-pager
sudo journalctl -u cloudflared -n 200 --no-pager
```

Periksa outbound TCP/UDP port 7844 dan koneksi internet server.

### Login selalu gagal setelah restart

Periksa apakah `LB_AUTO_SECRET` berubah. Token login lama menjadi tidak valid ketika secret berubah; user cukup login ulang. Jangan mengganti secret pada setiap restart.

### Fonnte tidak mengirim pesan

```bash
sudo journalctl -u lb-auto -n 200 --no-pager
```

Kemudian periksa dari aplikasi:

1. Login sebagai Owner.
2. Buka User Management.
3. Pastikan nomor role tujuan menggunakan format `62`.
4. Tekan ikon lonceng untuk melihat status notifikasi.
5. Pastikan token Fonnte pada `/etc/lb-auto/lb-auto.env` masih aktif.

Setelah mengubah environment:

```bash
sudo systemctl restart lb-auto.service
```

### Upload gagal

Periksa permission:

```bash
test -w /opt/lb-auto/uploads
ls -ld /opt/lb-auto/uploads
```

Jika folder belum ada:

```bash
sudo install -d -o "$(id -un)" -g "$(id -gn)" -m 0750 /opt/lb-auto/uploads
sudo systemctl restart lb-auto
```

### Database terkunci

Pastikan service hanya menggunakan satu worker:

```bash
systemctl cat lb-auto.service
```

`ExecStart` harus memuat:

```text
--workers 1
```

Jika kebutuhan concurrency atau jumlah user meningkat signifikan, rencanakan migrasi database dari SQLite ke PostgreSQL sebelum menambah worker atau beberapa server aplikasi.

## 21. Checklist go-live

### Server

- [ ] Aplikasi berada di `/opt/lb-auto`.
- [ ] Repository berasal dari `git@github.com:NicoIzumi30/lb-auto.git`.
- [ ] Service berjalan sebagai user Linux deployment, bukan root.
- [ ] Virtual environment dan dependency terpasang.
- [ ] `lb-auto.service` enabled dan active.
- [ ] Uvicorn bind ke `127.0.0.1:8542`.
- [ ] Hanya satu worker Uvicorn.
- [ ] Port 8542 tidak dibuka pada firewall.

### Rahasia dan akun

- [ ] `LB_AUTO_SECRET` sudah acak dan disimpan aman.
- [ ] Token Fonnte sudah dirotasi.
- [ ] Environment file memiliki mode `600`.
- [ ] Password seluruh akun bawaan sudah diganti.
- [ ] Akun Owner dapat login menggunakan password produksi.
- [ ] Nomor WhatsApp approver sudah dikonfigurasi.

### Cloudflare

- [ ] `cloudflared.service` enabled dan active.
- [ ] Tunnel berstatus `Healthy`.
- [ ] Public hostname menuju `http://127.0.0.1:8542`.
- [ ] HTTPS aktif.
- [ ] Cloudflare Access melindungi hostname.
- [ ] Policy Access hanya mengizinkan staf terkait.
- [ ] Cache bypass untuk API dan uploads.
- [ ] Rate limit login sudah disiapkan.

### Data

- [ ] Backup database berhasil diuji.
- [ ] Backup uploads berhasil diuji.
- [ ] Timer backup aktif.
- [ ] Salinan backup tersedia di storage lain.
- [ ] Restore pernah diuji pada lingkungan non-production.

### Pengujian akhir

- [ ] Health endpoint lokal berhasil.
- [ ] Domain publik dapat dibuka dari jaringan lain.
- [ ] Login Cloudflare Access berhasil.
- [ ] Login aplikasi berhasil.
- [ ] Upload foto berhasil.
- [ ] Notifikasi WhatsApp approval berhasil.
- [ ] PWA dapat dipasang pada ponsel.
- [ ] Flow satu unit diuji dari awal sampai delivery.

## 22. File deployment yang tersedia

| File | Fungsi |
| --- | --- |
| `deploy/lb-auto.service` | Menjalankan FastAPI melalui systemd |
| `deploy/lb-auto.env.example` | Template environment produksi |
| `deploy/backup-lb-auto.sh` | Backup SQLite dan uploads |
| `deploy/lb-auto-backup.service` | One-shot backup service |
| `deploy/lb-auto-backup.timer` | Jadwal backup harian |
| `backend/admin.py` | CLI pengaturan password dan status akun aplikasi |

## 23. Urutan deployment singkat

```text
1. Siapkan server dan SSH key GitHub pada user Linux deployment
2. Clone git@github.com:NicoIzumi30/lb-auto.git ke /opt/lb-auto
3. Buat virtual environment dan instal dependency
4. Buat /etc/lb-auto/lb-auto.env
5. Inisialisasi database
6. Ganti password akun yang tersedia
7. Generate, pasang, dan tes lb-auto.service dengan user Linux deployment
8. Pastikan origin hanya di 127.0.0.1:8542
9. Buat Cloudflare Tunnel
10. Pasang cloudflared.service
11. Route domain ke http://127.0.0.1:8542
12. Aktifkan Cloudflare Access dan security rules
13. Pasang backup timer
14. Uji domain, login, upload, WA, dan full flow
15. Go live
```
