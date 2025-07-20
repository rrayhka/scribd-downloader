import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def find_brave_path():
    """Mencari path Brave browser secara otomatis"""
    possible_paths = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        # r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        # os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
        # r"C:\Users\%USERNAME%\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"
    ]
    
    for path in possible_paths:
        expanded_path = os.path.expandvars(path)
        if os.path.exists(expanded_path):
            return expanded_path
    
    return None

# 1. Persiapan Data
df = pd.read_csv('output.csv', sep=',')
urls = df['URL'].drop_duplicates().tolist()

# 2. Automasi Browser dengan Brave
print("🔍 Mencari instalasi Brave browser...")
brave_path = find_brave_path()

if not brave_path:
    print("❌ Brave browser tidak ditemukan!")
    print("💡 Pastikan Brave sudah terinstall atau sesuaikan path secara manual:")
    print("   brave_path = r'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'")
    exit(1)

print(f"✅ Brave ditemukan di: {brave_path}")

options = Options()
options.binary_location = brave_path
options.add_argument('--no-first-run')
options.add_argument('--no-service-autorun') 
options.add_argument('--password-store=basic')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

try:
    # Inisialisasi driver dengan Brave
    print("🚀 Menginisialisasi Brave browser...")
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 20)
    print("✅ Brave browser berhasil diinisialisasi")
    print(f"🔍 Memproses {len(urls)} URL...")
    
except Exception as e:
    print(f"❌ Gagal menginisialisasi Brave browser: {e}")
    exit(1)

for i, url in enumerate(urls, 1):
    try:
        print(f"\n📥 Memproses URL {i}/{len(urls)}: {url}")
        
        # Kunjungi halaman utama
        driver.get("https://mydocdownloader.com/")

        # Temukan <div class="input-box"> lalu cari input-nya
        input_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.input-box input')))
        input_box.clear()
        input_box.send_keys(url)

        # Klik tombol submit
        input_box.send_keys(Keys.RETURN)

        # Tunggu redirect ke halaman compress-pdf
        wait.until(EC.url_contains("https://compress-pdf.vietdreamhouse.com/"))
        print("✅ Berhasil redirect ke halaman download")

        # Tunggu file disiapkan (±10 detik)
        print("⏳ Menunggu file disiapkan...")
        time.sleep(10)

        # Cari tombol download dan klik
        download_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn.btn-lg.btn-success')))
        download_link = download_btn.get_attribute('href')
        
        if download_link:
            print(f"🔗 Download link: {download_link}")
            driver.get(download_link)  # Ini akan memicu unduhan
            print("✅ Download dimulai")
        else:
            print(f"❌ Tidak dapat menemukan download link untuk URL: {url}")
            continue

        # Tunggu beberapa detik sebelum lanjut
        time.sleep(5)

    except Exception as e:
        print(f"❌ Gagal untuk URL: {url} - {e}")
        continue

print("\n🎉 Semua URL telah diproses!")
driver.quit()
