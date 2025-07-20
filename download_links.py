import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Persiapan Data
df = pd.read_csv('sample.csv', sep=',')
urls = df['URL'].drop_duplicates().tolist()

# 2. Automasi Browser
options = uc.ChromeOptions()
options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 20)

for url in urls:
    try:
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

        # Tunggu file disiapkan (±10 detik)
        time.sleep(10)

        # Cari tombol download dan klik
        download_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn.btn-lg.btn-success')))
        download_link = download_btn.get_attribute('href')
        print(f"🔗 Download link: {download_link}")
        driver.get(download_link)  # Ini akan memicu unduhan

        # Tunggu beberapa detik sebelum lanjut
        time.sleep(5)

    except Exception as e:
        print(f"❌ Gagal untuk URL: {url} - {e}")
        continue

driver.quit()
