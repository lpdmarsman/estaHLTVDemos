import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import shutil

def setup_driver(headless=False, download_path=None):
    """Setup and return Chrome WebDriver with download preferences."""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set download preferences
    if download_path:
        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def create_download_folder():
    """Create hltv_demos folder if it doesn't exist."""
    folder_path = os.path.abspath("hltv_demos")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def read_urls(filename="all_match_download_url.txt"):
    """Read URLs from file."""
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            urls = [line.strip() for line in file if line.strip()]
            print(f"Found {len(urls)} URLs to process.")
            return urls
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def handle_cookie_banner(driver):
    """Handle cookie consent banner if present."""
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonDecline"))
        )
        cookie_button.click()
        time.sleep(1)
        print("Cookie banner handled.")
    except:
        pass

def get_filename_from_url(url):
    """Extract filename from URL or generate one."""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    
    # If no filename in URL, generate one
    if not filename or '.' not in filename:
        # Extract match ID or use timestamp
        if 'download' in url and 'demoid' in url:
            demo_id = url.split('demoid=')[-1].split('&')[0]
            filename = f"demo_{demo_id}.dem"
        else:
            filename = f"demo_{int(time.time())}.dem"
    
    return filename

def download_file_requests(url, download_path, filename):
    """Download file using requests library."""
    try:
        print(f"Downloading {filename}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        file_path = os.path.join(download_path, filename)
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(file_path)
        print(f"Downloaded {filename} ({file_size} bytes)")
        return True
        
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def wait_for_download_selenium(download_path, timeout=None):
    """Wait for download to complete when using Selenium."""
    start_time = time.time()
    
    while timeout is None or  time.time() - start_time < timeout:
        # Check for .crdownload files (Chrome partial downloads)
        temp_files = [f for f in os.listdir(download_path) if f.endswith('.crdownload')]
        if not temp_files:
            # No partial downloads, check if any new files were created
            files = os.listdir(download_path)
            if files:
                return True
        time.sleep(1)
    
    return False

def process_download_url_with_fresh_driver(url, download_path, headless=False):
    """Process single download URL with a fresh driver instance."""
    driver = None
    try:
        print(f"\nProcessing: {url}")
        
        # # First try with requests (faster and more reliable)
        # filename = get_filename_from_url(url)
        # if download_file_requests(url, download_path, filename):
        #     return True
        
        # print("Requests method failed, trying with Selenium...")
        
        # Fallback to Selenium
        driver = setup_driver(headless, download_path)
        
        # Navigate to URL
        driver.get(url)
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Handle cookie consent banner
        handle_cookie_banner(driver)
        
        # The navigation to the URL should trigger the download
        # Wait for download to complete
        if wait_for_download_selenium(download_path):
            print("Download completed via Selenium")
            return True
        else:
            print("Download timeout via Selenium")
            return False
            
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    """Main function."""
    # headless_input = input("Run in headless mode? (y/n) [default: n]: ").strip().lower()
    # headless = headless_input in ['y', 'yes']
    # headless = False
    headless = True
    
    # wait_input = input("Wait time between downloads (seconds) [default: 5]: ").strip()
    wait_input = "5"
    try:
        wait_time = int(wait_input) if wait_input else 5
    except ValueError:
        wait_time = 5
    
    # interactive_input = input("Interactive mode? (y/n) [default: n]: ").strip().lower()
    # interactive = interactive_input in ['y', 'yes']
    interactive = False
    
    # Create download folder
    download_path = create_download_folder()
    print(f"Downloads will be saved to: {download_path}")
    
    # Read URLs from file
    filename = "all_match_download_url.txt"
    urls = read_urls(filename)
    
    if not urls:
        print("No URLs found. Please check the file 'all_match_download_url.txt'")
        return
    
    successful_downloads = 0
    failed_downloads = 0
    
    try:
        for i, url in enumerate(urls, 1):
            print(f"\n{'='*60}")
            print(f"Processing {i}/{len(urls)}")
            
            # Process URL with fresh driver
            success = process_download_url_with_fresh_driver(url, download_path, headless)
            
            if success:
                successful_downloads += 1
            else:
                failed_downloads += 1
            
            if interactive:
                user_input = input(f"\nPress Enter to continue (or 'q' to quit): ").strip().lower()
                if user_input == 'q':
                    break
            
            # Wait between downloads (except for last one)
            if i < len(urls):
                print(f"Waiting {wait_time} seconds before next download...")
                time.sleep(wait_time)
        
        # Summary
        print(f"\n{'='*60}")
        print("Download Summary:")
        print(f"Successful downloads: {successful_downloads}")
        print(f"Failed downloads: {failed_downloads}")
        print(f"Total processed: {successful_downloads + failed_downloads}")
        print(f"Files saved to: {download_path}")
        
        # List downloaded files
        demo_files = [f for f in os.listdir(download_path) if f.endswith('.dem')]
        if demo_files:
            print(f"\nDownloaded demo files:")
            for demo_file in demo_files:
                file_path = os.path.join(download_path, demo_file)
                file_size = os.path.getsize(file_path)
                print(f"  - {demo_file} ({file_size} bytes)")
        
    except KeyboardInterrupt:
        print("\nDownload interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()