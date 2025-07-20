# Scribd Downloader

🚀 **Automated Scribd Document Downloader & Link Extractor**

Sebuah tool otomatis untuk mencari dan mengunduh dokumen dari Scribd menggunakan Google Search dan web scraping. Tool ini terdiri dari dua komponen utama: pencarian link Scribd dan pengunduhan dokumen otomatis.

## 📋 Daftar Isi

- [Fitur](#-fitur)
- [Komponen](#-komponen)
- [Instalasi](#-instalasi)
- [Penggunaan](#-penggunaan)
  - [1. Mencari Link Scribd](#1-mencari-link-scribd)
  - [2. Mengunduh Dokumen](#2-mengunduh-dokumen)
- [Format File Input](#-format-file-input)
- [Troubleshooting](#-troubleshooting)
- [Disclaimer](#-disclaimer)
- [Kontribusi](#-kontribusi)

## ✨ Fitur

- **Pencarian Otomatis**: Mencari link Scribd menggunakan Google Search dengan query kustom
- **Anti-Detection**: Menggunakan `undetected-chromedriver` untuk menghindari deteksi bot
- **Batch Download**: Mengunduh multiple dokumen sekaligus dari file CSV
- **Error Handling**: Penanganan error yang robust dengan retry mechanism
- **Progress Tracking**: Monitoring progress download dengan logging detail
- **Duplicate Detection**: Mencegah duplikasi link saat scraping
- **CAPTCHA Support**: Dukungan manual CAPTCHA solving

## 🔧 Komponen

### 1. `scrape_links.py` - Scribd Link Extractor

Tool untuk mencari dan mengekstrak link Scribd dari hasil Google Search.

**Fitur Utama:**

- Google Search automation dengan Selenium
- Ekstraksi link Scribd dengan BeautifulSoup
- Export hasil ke CSV
- Anti-bot detection
- Multiple page scraping
- Random delay antar request

### 2. `download_links.py` - Document Downloader

Tool untuk mengunduh dokumen Scribd secara otomatis menggunakan layanan pihak ketiga.

**Fitur Utama:**

- Batch download dari file CSV
- Automasi browser untuk interaksi dengan mydocdownloader.com
- Progress monitoring
- Error handling dan retry
- Download link extraction

## 🛠 Instalasi

### Prerequisites

- Python 3.7+
- Google Chrome browser
- Internet connection

### Install Dependencies

```bash
# Clone repository
git clone https://github.com/rrayhka/scribd-downloader.git
cd scribd-downloader

# Install all required packages from requirements.txt
pip install -r requirements.txt
```

**Alternatif Manual Install:**

```bash
# Install individual packages
pip install pandas undetected-chromedriver selenium beautifulsoup4 fake-useragent
```

### Dependencies Detail

File `requirements.txt` berisi:

```
pandas>=1.3.0
selenium>=4.15.0
undetected-chromedriver>=3.5.0
beautifulsoup4>=4.9.0
fake-useragent>=1.4.0
```

## 📖 Penggunaan

### 1. Mencari Link Scribd

Gunakan `scrape_links.py` untuk mencari link Scribd dari Google Search:

#### Basic Usage

```bash
python scrape_links.py "Soal CPNS"
```

#### Advanced Usage

```bash
# Scrape 5 halaman hasil pencarian
python scrape_links.py "Soal CPNS" --pages 5

# Simpan hasil ke file CSV
python scrape_links.py "Soal CPNS" --pages 3 --output output.csv

# Mode visible browser (tidak headless)
python scrape_links.py "Soal CPNS" --no-headless --pages 2

# Custom delay antar request
python scrape_links.py "Soal CPNS" --delay-min 5 --delay-max 10
```

#### Parameter Lengkap

```bash
python scrape_links.py [QUERY] [OPTIONS]

Options:
  --pages, -p          Jumlah halaman yang akan di-scrape (default: 1)
  --start, -s          Index awal hasil pencarian (default: 0)
  --results-per-page   Jumlah hasil per halaman (default: 10)
  --output, -o         File output untuk menyimpan hasil (format CSV)
  --delay-min          Delay minimum antar request dalam detik (default: 3.0)
  --delay-max          Delay maksimum antar request dalam detik (default: 7.0)
  --no-headless        Jalankan Chrome dalam mode visible
  --verbose            Tampilkan informasi debug detail
```

### 2. Mengunduh Dokumen

Gunakan `download_links.py` untuk mengunduh dokumen dari link yang sudah dikumpulkan:

#### Persiapan File CSV

Gunakan file `output.csv` dari hasil scrapping:

```csv
Title,URL
To CPNS 24 (Special Edition) 4,https://www.scribd.com/document/779719573/TO-CPNS-24-SPECIAL-EDITION-4
Latihan Soal Cpns 2023 Hots (Twk-Tiu-Tkp) Catbkn Dotcom,https://www.scribd.com/document/622386409/Latihan-Soal-Cpns-2023-Hots-Twk-tiu-tkp-Catbkn-Dotcom
```

#### Menjalankan Download

```bash
python download_links.py
```

Script akan:

1. Membaca file `output.csv`
2. Mengunjungi mydocdownloader.com untuk setiap URL
3. Mengotomatisasi proses download
4. Menyimpan file ke folder download default browser

## 🔍 Troubleshooting

### 1. Chrome Driver Issues

```bash
# Error: ChromeDriver executable not found
# Solusi: Install ulang undetected-chromedriver
pip uninstall undetected-chromedriver
pip install undetected-chromedriver
```

### 2. CAPTCHA Errors

- Jika muncul CAPTCHA, gunakan mode `--no-headless`
- Solve CAPTCHA secara manual di browser
- Script akan menunggu hingga 30 detik

### 3. No Links Found

- Periksa koneksi internet
- Coba query pencarian yang lebih spesifik
- Gunakan `--verbose` untuk debug detail
- Periksa file `debug_page_*.html` yang di-generate

### 4. Download Failures

- Pastikan URL Scribd valid dan dapat diakses
- Periksa format file CSV
- Cek koneksi ke mydocdownloader.com

### 5. Rate Limiting

- Tambah delay dengan `--delay-min` dan `--delay-max`
- Kurangi jumlah pages yang di-scrape
- Gunakan mode `--no-headless` untuk monitoring

## ⚠️ Disclaimer

**PENTING**: Tool ini dibuat untuk tujuan edukasi dan penelitian. Pengguna bertanggung jawab penuh atas penggunaan tool ini. Pastikan untuk:

- ✅ Menghormati Terms of Service dari Scribd
- ✅ Menggunakan hanya untuk konten yang legal
- ✅ Tidak melakukan spam atau abuse
- ✅ Menghormati hak cipta penulis
- ✅ Menggunakan dengan rate limiting yang wajar

**Pengembang tidak bertanggung jawab atas penyalahgunaan tool ini.**

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan:

1. Fork repository ini
2. Buat branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request
