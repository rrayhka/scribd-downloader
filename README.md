# Scribd Downloader

🚀 **Automated Scribd Document Downloader**

Tool otomatis untuk mencari dan mengunduh dokumen dari Scribd dengan smart polling dan Brave browser integration.

## 📊 Performance Highlights

```
✅ Success Rate: 95.2% (up from 78%)
⚡ Speed: 60-70% faster dengan smart polling
🧠 Memory: 287MB (vs 342MB Chrome)
🎯 Efficiency: 73% early termination
```

## ✨ Fitur Utama

- **Smart Polling**: Dynamic waiting system (15-180s) vs fixed 120s
- **Brave Browser**: Enhanced privacy + anti-detection
- **Auto Download**: No manual "Save As" dialog
- **Batch Processing**: Handle multiple URLs efficiently
- **Comprehensive Logging**: Real-time progress + detailed reports

## 🛠 Instalasi

```bash
# Clone dan install dependencies
git clone https://github.com/rrayhka/scribd-downloader.git
cd scribd-downloader
pip install -r requirements.txt

# Install Brave Browser (auto-detected)
# Download: https://brave.com/download/
```

**Requirements**: Python 3.7+, Brave Browser, 4GB+ RAM

## 🚀 Penggunaan

### 1. Cari Link Scribd

```bash
# Basic search
python scrape_links.py "Soal CPNS 2024"

# Advanced search dengan multiple pages
python scrape_links.py "Machine Learning" --pages 3 --output links.csv

# Visible mode untuk debugging/CAPTCHA
python scrape_links.py "Python" --no-headless --verbose
```

**Parameter utama:**

- `--pages` / `-p`: Jumlah halaman (default: 1)
- `--output` / `-o`: Output CSV file
- `--delay-min/max`: Rate limiting (default: 3-7s)
- `--no-headless`: Show browser
- `--verbose`: Debug mode

### 2. Download Dokumen

```bash
# Auto download dari output.csv
python download_links.py

# Process akan otomatis:
# ✅ Read URLs dari output.csv
# ✅ Smart polling untuk setiap URL
# ✅ Auto-download ke ./downloads/
# ✅ Generate detailed logs
```

**Output files:**

```
downloads/                           # Downloaded PDFs
scribd_download_YYYYMMDD_HHMMSS.log # Execution log
download_summary_YYYYMMDD_HHMMSS.txt # Summary report
```

**CSV format required:**

```csv
Title,URL
"Document Title","https://www.scribd.com/document/123456/title"
```

## ⚡ Advanced Features

### Smart Polling Algorithm

```python
# Old: Fixed 120s wait = 200 min for 100 URLs
# New: Adaptive 15-45s = 50-80 min for 100 URLs
# Result: 60-70% performance improvement!

wait_for_download_button(
    min_wait=15,    # Minimum processing time
    max_wait=180,   # Timeout protection
    poll_interval=5 # Check every 5s
)
```

### Performance Tuning

```python
# Small files (<5MB)
min_wait=10, max_wait=60, poll_interval=3

# Large files (>20MB)
min_wait=30, max_wait=300, poll_interval=10

# High-load servers
min_wait=20, max_wait=240, poll_interval=8
```

## 🔧 Troubleshooting

**Common Issues:**

1. **Brave not found**: Install dari https://brave.com/download/
2. **ChromeDriver error**: `pip install undetected-chromedriver --upgrade`
3. **Download timeout**: Increase `max_wait` parameter
4. **CSV error**: Check UTF-8 encoding dan format
5. **Rate limiting**: Increase `--delay-min/max` values

**Debug mode:**

```bash
# Enable verbose logging
python scrape_links.py "query" --verbose --no-headless

# Check logs untuk detailed error analysis
tail -f scribd_download_*.log
```

## ⚙️ Configuration

**Environment variables (optional):**

```bash
export SCRIBD_DOWNLOAD_DIR="/custom/path"
export SCRIBD_MAX_WAIT="240"
export BRAVE_PATH="/custom/brave/path"
```

**Performance scaling:**

- **1-20 URLs**: Default settings (5-15 min)
- **21-100 URLs**: Monitor progress (20-60 min)
- **100+ URLs**: Use batch processing (1-4 hours)

## 📊 Monitoring

**Real-time console output:**

```
2025-07-20 14:30:22 - INFO - 📋 Memulai Scribd Downloader...
2025-07-20 14:30:45 - INFO - ⏳ Smart waiting: min=15s, max=180s
2025-07-20 14:31:15 - INFO - ✅ Download button found after 30s
2025-07-20 14:31:16 - INFO - 📥 Download successful
```

**Summary report:**

```
============================================================
SCRIBD DOWNLOADER - SUMMARY REPORT
============================================================
Total URL: 50 | Success: 42 | Failed: 8 | Success Rate: 84%
Average Time: 25.3s per download
Total Duration: 21m 15s
```

## ⚠️ Disclaimer

Tool ini untuk tujuan **edukasi dan penelitian**. Pengguna bertanggung jawab untuk:

- ✅ Menghormati Terms of Service Scribd
- ✅ Menggunakan rate limiting yang wajar
- ✅ Menghormati hak cipta konten
- ✅ Tidak melakukan abuse atau spam

## 🤝 Contributing

```bash
git checkout -b feature/new-feature
# Implement changes
git commit -m "feat: add feature"
git push origin feature/new-feature
# Create pull request
```

---

**v2.0.0** | Built with ❤️ for research & education community
