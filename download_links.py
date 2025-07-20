import time
import pandas as pd
import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging configuration
def setup_logging():
    """Setup logging configuration with both file and console output"""
    log_filename = f"scribd_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger, log_filename

# Initialize logging
logger, log_file = setup_logging()

def generate_summary_report(total_urls, successful, failed, errors, download_dir, log_file):
    """Generate a summary report file"""
    report_filename = f"download_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("SCRIBD DOWNLOADER - SUMMARY REPORT\n")
        f.write("=" * 60 + "\n")
        f.write(f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total URL: {total_urls}\n")
        f.write(f"Berhasil: {successful}\n")
        f.write(f"Gagal: {failed}\n")
        f.write(f"Success Rate: {(successful/total_urls*100):.1f}%\n")
        f.write(f"Download Directory: {download_dir}\n")
        f.write(f"Log File: {log_file}\n\n")
        
        if errors:
            f.write("DETAIL ERROR:\n")
            f.write("-" * 40 + "\n")
            for i, error in enumerate(errors, 1):
                f.write(f"{i}. URL: {error['url']}\n")
                f.write(f"   Error: {error['error']}\n\n")
        else:
            f.write("Tidak ada error yang tercatat.\n")
        
        f.write("=" * 60 + "\n")
        f.write("Report selesai.\n")
    
    return report_filename

def find_brave_path():
    """Mencari path Brave browser secara otomatis"""
    possible_paths = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
        r"C:\Users\%USERNAME%\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"
    ]
    
    for path in possible_paths:
        expanded_path = os.path.expandvars(path)
        if os.path.exists(expanded_path):
            return expanded_path
    
    return None

def wait_for_download_button(driver, min_wait=10, max_wait=20, poll_interval=3):
    """
    Smart polling untuk menunggu tombol download tersedia
    
    Args:
        driver: Selenium WebDriver instance
        min_wait: Waktu tunggu minimum dalam detik
        max_wait: Waktu tunggu maksimum dalam detik  
        poll_interval: Interval polling dalam detik
        
    Returns:
        tuple: (success, download_button, elapsed_time)
    """
    logger.info(f"⏳ Smart waiting: min={min_wait}s, max={max_wait}s, interval={poll_interval}s")
    
    # Tunggu minimum (file perlu waktu untuk diproses)
    logger.info(f"🕐 Menunggu waktu minimum: {min_wait} detik...")
    time.sleep(min_wait)
    
    # Mulai polling
    elapsed_time = min_wait
    logger.info(f"🔄 Memulai polling untuk tombol download...")
    
    while elapsed_time < max_wait:
        try:
            # Coba temukan tombol download
            download_btn = driver.find_element(By.CSS_SELECTOR, 'a.btn.btn-lg.btn-success')
            
            # Validasi tombol tersedia dan clickable
            if download_btn and download_btn.is_enabled() and download_btn.is_displayed():
                href = download_btn.get_attribute('href')
                if href and href.strip():  # Pastikan href tidak kosong
                    logger.info(f"✅ Tombol download valid ditemukan setelah {elapsed_time} detik")
                    return True, download_btn, elapsed_time
                    
        except Exception as e:
            # Tombol belum tersedia atau error lain
            logger.debug(f"Polling attempt failed: {e}")
        
        # Progress indicator
        remaining = max_wait - elapsed_time
        logger.info(f"⏳ Polling... {elapsed_time}s elapsed, {remaining}s remaining")
        
        # Tunggu sebelum polling berikutnya
        time.sleep(poll_interval)
        elapsed_time += poll_interval
    
    # Timeout reached
    logger.warning(f"⏰ Timeout: Tombol download tidak ditemukan setelah {max_wait} detik")
    return False, None, elapsed_time

def main():
    # 1. Persiapan Data
    logger.info("📋 Memulai Scribd Downloader...")
    logger.info(f"📂 Log file: {log_file}")

    try:
        df = pd.read_csv('output.csv', sep=',')
        urls = df['URL'].drop_duplicates().tolist()
        logger.info(f"📄 Berhasil membaca {len(df)} baris dari output.csv")
        logger.info(f"🔗 Ditemukan {len(urls)} URL unik untuk diproses")
    except Exception as e:
        logger.error(f"❌ Gagal membaca file CSV: {e}")
        exit(1)

    # 2. Automasi Browser dengan Brave
    logger.info("🔍 Mencari instalasi Brave browser...")
    brave_path = find_brave_path()

    if not brave_path:
        logger.error("❌ Brave browser tidak ditemukan!")
        logger.error("💡 Pastikan Brave sudah terinstall atau sesuaikan path secara manual:")
        logger.error("   brave_path = r'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'")
        exit(1)

    logger.info(f"✅ Brave ditemukan di: {brave_path}")

    options = Options()
    options.binary_location = brave_path

    # SOLUSI UTAMA: Konfigurasi download otomatis
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)
    logger.info(f"📁 Download directory: {download_dir}")

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,  # Disable "Save As" dialog
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
        "plugins.always_open_pdf_externally": True,  # Download PDF instead of opening
    }
    options.add_experimental_option("prefs", prefs)
    logger.info("⚙️ Browser preferences configured for automatic download")

    # Anti-detection options
    options.add_argument('--no-first-run')
    options.add_argument('--no-service-autorun') 
    options.add_argument('--password-store=basic')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    logger.info("🛡️ Anti-detection options applied")

    # Initialize counters for summary
    successful_downloads = 0
    failed_downloads = 0
    download_errors = []

    try:
        # Inisialisasi driver dengan Brave
        logger.info("🚀 Menginisialisasi Brave browser...")
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        wait = WebDriverWait(driver, 20)
        logger.info("✅ Brave browser berhasil diinisialisasi")
        logger.info(f"📁 Download directory: {download_dir}")
        logger.info(f"🔍 Memproses {len(urls)} URL...")
        
    except Exception as e:
        logger.error(f"❌ Gagal menginisialisasi Brave browser: {e}")
        exit(1)

    # Process each URL
    for i, url in enumerate(urls, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"📥 Memproses URL {i}/{len(urls)}")
        logger.info(f"🔗 URL: {url}")
        
        try:
            # Kunjungi halaman utama
            logger.info("🌐 Mengunjungi mydocdownloader.com...")
            driver.get("https://mydocdownloader.com/")

            # Temukan <div class="input-box"> lalu cari input-nya
            logger.info("🔍 Mencari input box...")
            input_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.input-box input')))
            input_box.clear()
            input_box.send_keys(url)
            logger.info("✍️ URL telah dimasukkan ke input box")

            # Klik tombol submit
            logger.info("📤 Mengirim form...")
            input_box.send_keys(Keys.RETURN)

            # Tunggu redirect ke halaman compress-pdf
            logger.info("⏳ Menunggu redirect ke halaman download...")
            wait.until(EC.url_contains("https://compress-pdf.vietdreamhouse.com/"))
            logger.info("✅ Berhasil redirect ke halaman download")

            # Smart waiting dengan polling dinamis untuk tombol download
            success, download_btn, elapsed_time = wait_for_download_button(
                driver, 
                min_wait=10,    # 10 detik minimum
                max_wait=30,   # 30 detik maksimum
                poll_interval=5 # cek setiap 5 detik
            )
            
            if not success:
                error_msg = f"❌ Timeout: Tombol download tidak tersedia setelah {elapsed_time} detik"
                logger.error(error_msg)
                failed_downloads += 1
                download_errors.append({"url": url, "error": f"Download button timeout after {elapsed_time}s"})
                continue

            # Dapatkan download link dari tombol yang sudah ditemukan
            logger.info("🔗 Mengekstrak download link...")
            if download_btn is not None:
                download_link = download_btn.get_attribute('href')
            else:
                download_link = None
            
            if download_link and download_link.strip():
                logger.info(f"🔗 Download link ditemukan: {download_link}")
                logger.info("📥 Memulai download...")
                driver.get(download_link)  # Ini akan memicu unduhan
                logger.info("✅ Download berhasil dimulai")
                successful_downloads += 1
                
                # Tunggu sebentar untuk memastikan download dimulai
                time.sleep(3)
                
            else:
                error_msg = f"❌ Download link kosong/tidak valid untuk URL: {url}"
                logger.error(error_msg)
                failed_downloads += 1
                download_errors.append({"url": url, "error": "Download link empty or invalid"})
                continue

            # Tunggu beberapa detik sebelum lanjut
            logger.info("⏳ Menunggu 5 detik sebelum URL berikutnya...")
            time.sleep(5)

        except Exception as e:
            error_msg = f"❌ Gagal memproses URL {url}: {str(e)}"
            logger.error(error_msg)
            failed_downloads += 1
            download_errors.append({"url": url, "error": str(e)})
            continue

    # Generate final summary
    logger.info(f"\n{'='*60}")
    logger.info("🎉 DOWNLOAD SELESAI - SUMMARY REPORT")
    logger.info(f"{'='*60}")
    logger.info(f"📊 Total URL diproses: {len(urls)}")
    logger.info(f"✅ Berhasil: {successful_downloads}")
    logger.info(f"❌ Gagal: {failed_downloads}")
    logger.info(f"📈 Success rate: {(successful_downloads/len(urls)*100):.1f}%")
    logger.info(f"📁 Download directory: {download_dir}")
    logger.info(f"📋 Log file: {log_file}")

    # Log detailed errors if any
    if download_errors:
        logger.info(f"\n📋 DETAIL ERROR REPORT:")
        for i, error in enumerate(download_errors, 1):
            logger.error(f"{i}. URL: {error['url']}")
            logger.error(f"   Error: {error['error']}")

    # Generate summary report file
    report_file = generate_summary_report(len(urls), successful_downloads, failed_downloads, download_errors, download_dir, log_file)
    logger.info(f"📄 Summary report saved: {report_file}")

    logger.info(f"\n✅ Semua proses selesai!")
    logger.info(f"📋 Log file: {log_file}")
    logger.info(f"📄 Summary report: {report_file}")

    # Close browser
    driver.quit()
    logger.info("🔒 Browser ditutup")

if __name__ == "__main__":
    main()
