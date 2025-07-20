import time
import pandas as pd
import os
import requests
from pathlib import Path
from urllib.parse import urlparse, unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'download_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScribdDownloader:
    def __init__(self, download_dir="downloads", headless=True, max_retries=3):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.headless = headless
        self.max_retries = max_retries
        self.driver = None
        self.wait = None
        self.session = requests.Session()
        
        # Setup requests session with proper headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def find_brave_path(self):
        """Mencari path Brave browser secara otomatis"""
        possible_paths = [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def setup_browser(self):
        """Setup Brave browser dengan konfigurasi download otomatis"""
        brave_path = self.find_brave_path()
        if not brave_path:
            raise Exception("Brave browser tidak ditemukan!")
        
        options = Options()
        options.binary_location = brave_path
        
        # Konfigurasi download otomatis - INI YANG PALING PENTING
        prefs = {
            "download.default_directory": str(self.download_dir.absolute()),
            "download.prompt_for_download": False,  # Disable "Save As" dialog
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "safebrowsing.disable_download_protection": True,
            "plugins.always_open_pdf_externally": True,  # Download PDF instead of opening
        }
        options.add_experimental_option("prefs", prefs)
        
        if self.headless:
            options.add_argument('--headless')
        
        # Anti-detection options
        options.add_argument('--no-first-run')
        options.add_argument('--no-service-autorun')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 30)
        
        logger.info(f"✅ Brave browser initialized. Download directory: {self.download_dir}")

    def extract_filename_from_url(self, url):
        """Extract filename from URL"""
        parsed = urlparse(url)
        filename = unquote(os.path.basename(parsed.path))
        if not filename or '.' not in filename:
            filename = f"document_{int(time.time())}.pdf"
        return filename

    def download_file_direct(self, download_url, filename):
        """Download file directly using requests (bypasses browser dialog)"""
        try:
            logger.info(f"📥 Downloading directly: {filename}")
            
            response = self.session.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            file_path = self.download_dir / filename
            
            # Handle duplicate filenames
            counter = 1
            original_stem = file_path.stem
            original_suffix = file_path.suffix
            while file_path.exists():
                file_path = self.download_dir / f"{original_stem}_{counter}{original_suffix}"
                counter += 1
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"✅ Downloaded: {file_path}")
            return True, str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Direct download failed: {e}")
            return False, str(e)

    def wait_for_download_complete(self, filename, timeout=60):
        """Wait for browser download to complete"""
        expected_file = self.download_dir / filename
        temp_file = self.download_dir / f"{filename}.crdownload"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if expected_file.exists() and not temp_file.exists():
                logger.info(f"✅ Browser download completed: {expected_file}")
                return True, str(expected_file)
            time.sleep(1)
        
        return False, "Download timeout"

    def process_url(self, url, max_retries=None):
        """Process single URL with retry mechanism"""
        if max_retries is None:
            max_retries = self.max_retries
            
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Attempt {attempt + 1}/{max_retries} for: {url}")
                
                # Step 1: Navigate to mydocdownloader
                self.driver.get("https://mydocdownloader.com/")
                
                # Step 2: Input URL
                input_box = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.input-box input'))
                )
                input_box.clear()
                input_box.send_keys(url)
                input_box.send_keys(Keys.RETURN)
                
                # Step 3: Wait for redirect
                self.wait.until(EC.url_contains("compress-pdf.vietdreamhouse.com"))
                logger.info("✅ Redirected to download page")
                
                # Step 4: Wait for file preparation
                time.sleep(12)  # Slightly longer wait
                
                # Step 5: Get download link
                download_btn = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn.btn-lg.btn-success'))
                )
                download_link = download_btn.get_attribute('href')
                
                if not download_link:
                    raise Exception("Download link not found")
                
                logger.info(f"🔗 Download link obtained: {download_link}")
                
                # Step 6: Extract filename
                filename = self.extract_filename_from_url(url)
                
                # Step 7: Try direct download first (more reliable)
                success, result = self.download_file_direct(download_link, filename)
                
                if success:
                    return True, result
                
                # Step 8: Fallback to browser download
                logger.info("📥 Fallback to browser download...")
                self.driver.get(download_link)
                
                # Wait for download to complete
                success, result = self.wait_for_download_complete(filename, timeout=60)
                
                if success:
                    return True, result
                else:
                    raise Exception(f"Download failed: {result}")
                    
            except (TimeoutException, WebDriverException) as e:
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)  # Wait before retry
                    continue
                else:
                    return False, f"All attempts failed. Last error: {e}"
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                return False, str(e)
        
        return False, "Max retries exceeded"

    def process_urls_batch(self, urls, batch_size=5):
        """Process URLs in batches to prevent memory issues"""
        total_urls = len(urls)
        successful_downloads = []
        failed_downloads = []
        
        logger.info(f"🚀 Starting batch processing of {total_urls} URLs")
        
        for i in range(0, total_urls, batch_size):
            batch = urls[i:i + batch_size]
            logger.info(f"📦 Processing batch {i//batch_size + 1} ({len(batch)} URLs)")
            
            for j, url in enumerate(batch, 1):
                global_index = i + j
                logger.info(f"\n📥 Processing URL {global_index}/{total_urls}: {url}")
                
                success, result = self.process_url(url)
                
                if success:
                    successful_downloads.append({'url': url, 'file': result})
                    logger.info(f"✅ Success: {result}")
                else:
                    failed_downloads.append({'url': url, 'error': result})
                    logger.error(f"❌ Failed: {result}")
                
                # Small delay between downloads
                time.sleep(2)
            
            # Longer delay between batches
            if i + batch_size < total_urls:
                logger.info("⏸️ Batch completed. Resting before next batch...")
                time.sleep(10)
        
        return successful_downloads, failed_downloads

    def generate_report(self, successful_downloads, failed_downloads):
        """Generate download report"""
        report_file = self.download_dir / f"download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== SCRIBD DOWNLOAD REPORT ===\n\n")
            f.write(f"Total Successful: {len(successful_downloads)}\n")
            f.write(f"Total Failed: {len(failed_downloads)}\n\n")
            
            f.write("=== SUCCESSFUL DOWNLOADS ===\n")
            for item in successful_downloads:
                f.write(f"✅ {item['url']} -> {item['file']}\n")
            
            f.write("\n=== FAILED DOWNLOADS ===\n")
            for item in failed_downloads:
                f.write(f"❌ {item['url']} -> {item['error']}\n")
        
        logger.info(f"📊 Report saved: {report_file}")

    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        self.session.close()

def main():
    # Configuration
    CSV_FILE = 'output.csv'
    DOWNLOAD_DIR = 'downloads'
    HEADLESS = False  # Set True for production
    MAX_RETRIES = 3
    BATCH_SIZE = 3  # Process 3 URLs at a time
    
    downloader = ScribdDownloader(
        download_dir=DOWNLOAD_DIR,
        headless=HEADLESS,
        max_retries=MAX_RETRIES
    )
    
    try:
        # Read URLs from CSV
        df = pd.read_csv(CSV_FILE)
        urls = df['URL'].drop_duplicates().tolist()
        
        logger.info(f"📋 Loaded {len(urls)} unique URLs from {CSV_FILE}")
        
        # Setup browser
        downloader.setup_browser()
        
        # Process URLs
        successful, failed = downloader.process_urls_batch(urls, batch_size=BATCH_SIZE)
        
        # Generate report
        downloader.generate_report(successful, failed)
        
        # Summary
        logger.info(f"\n🎉 DOWNLOAD COMPLETE!")
        logger.info(f"✅ Successful: {len(successful)}")
        logger.info(f"❌ Failed: {len(failed)}")
        logger.info(f"📁 Files saved to: {downloader.download_dir}")
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
    finally:
        downloader.close()

if __name__ == "__main__":
    main()
