import os
import time
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def wait_for_download(folder: str, timeout: int = 30) -> str | None:
    """Wait for a .zip file to appear in the folder, return its path or None."""
    for _ in range(timeout):
        files = glob.glob(os.path.join(folder, "*.zip"))
        if files:
            return files[0]
        time.sleep(1)
    return None

# ✅ Set download path to Desktop/stuff
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
download_dir = os.path.join(desktop_path, "stuff")
os.makedirs(download_dir, exist_ok=True)

# ✅ Chrome options to simulate a real user
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
})
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)
# ❌ Do NOT run headless — Cloudflare will block you

# ✅ Start Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

#######################
websites = ["https://www.hltv.org/download/demo/70064", "https://www.hltv.org/download/demo/68282"]
for website in websites: 
# ✅ Open the HLTV demo download page
    print("Opening download page...")
    driver.get(website)
    # driver.get("https://www.hltv.org/download/demo/70064")

    # ✅ Wait for download to appear
    print("Waiting for download to start...")
    downloaded_file = wait_for_download(download_dir)
    time.sleep(100)
#######################

driver.quit()

# ✅ Check if download succeeded
if downloaded_file:
    print(f"✅ Download succeeded: {downloaded_file}")
else:
    print("❌ Download failed or timed out.")
