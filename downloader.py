import lzma
import json
from typing import Any, List, Union

import os
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# def find_match_ids(data: Union[dict, list]) -> List[Any]:
#     """Recursively search for all occurrences of 'Match ID' in the given JSON structure."""
#     match_ids: List[Any] = []

#     def recursive_search(obj: Any) -> None:
#         if isinstance(obj, dict):
#             for key, value in obj.items():
#                 if key == "hltvUrl":
#                     match_ids.append(value)
#                 else:
#                     recursive_search(value)
#         elif isinstance(obj, list):
#             for item in obj:
#                 recursive_search(item)

#     recursive_search(data)
#     return match_ids


# def main() -> None:
#     """Main function to decompress, parse, and extract Match IDs."""
#     file_path: str = "compressed_files/0a5fb56f-de83-4e4c-8f9d-bf6f24d7f54a.json.xz"

#     # Step 1: Decompress the .xz file
#     with lzma.open(file_path, "rt", encoding="utf-8") as file:
#         decompressed_data: str = file.read()

#     # Step 2: Load the JSON data
#     json_data: Any = json.loads(decompressed_data)

#     # print(json_data)

#     # Step 3: Find and print Match ID(s)
#     match_ids: List[Any] = find_match_ids(json_data)

#     if match_ids:
#         print("Match ID(s) found:")
#         for match_id in match_ids:
#             print(match_id)
#     else:
#         print("No 'Match ID' found.")

# if __name__ == "__main__":
#     main()

DRIVER_LOCATION = "chromedriver-win64/chromedriver-win64/chromedriver.exe"

def download_hltv_demos(
    match_url: str = "https://www.hltv.org/matches/2354343/wisla-krakow-vs-fnatic-iem-katowice-2022-play-in",
    download_dir: Optional[str] = None
) -> None:
    """
    Download demo files from a given HLTV match page using Selenium.

    Args:
        match_url (str): URL of the HLTV match page.
        download_dir (Optional[str]): Directory to save the downloaded demos.
    """
    if download_dir is None:
        download_dir = os.path.join(os.getcwd(), "hltv_demos")

    os.makedirs(download_dir, exist_ok=True)
    print(f"Download directory: {download_dir}")

    # Chrome options configuration
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,  # Disable safe browsing that might block downloads
        "safebrowsing.disable_download_protection": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2  # Don't load images to speed up
    })
    # Remove headless mode to see what's happening
    # chrome_options.add_argument("--headless=new")  # Commented out for debugging
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Use the correct driver path
    service = Service(executable_path=DRIVER_LOCATION)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Execute script to hide webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        print(f"Loading page: {match_url}")
        driver.get(match_url)
        
        # Wait for page to load properly
        wait = WebDriverWait(driver, 15)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        
        # Additional wait for dynamic content
        time.sleep(5)  # Increased wait time
        
        # Scroll to bottom to ensure all content is loaded
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Updated selectors specifically for HLTV demo links
        demo_selectors = [
            # Primary selector for HLTV demo links with data-demo-link attribute
            "//a[@data-demo-link-button]",
            "//a[contains(@data-demo-link, '/download/demo')]",
            "//a[@class='stream-box'][@data-demo-link-button]",
            
            # Fallback selectors
            "//a[contains(@href, '/download/demo')]",
            "//a[contains(@data-demo-link, 'demo')]",
            "//a[@data-demo-link]",
            
            # Additional fallback selectors
            "//a[contains(text(), 'Demo')]",
            "//div[contains(text(), 'Demo')]/..//a",
            "//div[contains(text(), 'GOTV')]/..//a",
        ]
        
        demo_links = []
        successful_selector = None
        
        for selector in demo_selectors:
            try:
                print(f"Trying selector: {selector}")
                links = driver.find_elements(By.XPATH, selector)
                if links:
                    demo_links.extend(links)
                    successful_selector = selector
                    print(f"✓ Found {len(links)} demo link(s) with selector: {selector}")
                    break
                else:
                    print(f"✗ No links found with selector: {selector}")
            except NoSuchElementException:
                print(f"✗ Selector failed: {selector}")
                continue
        
        if not demo_links:
            print("\nNo demo links found with any selector.")
            print("Debugging information:")
            print(f"Page title: {driver.title}")
            print(f"Current URL: {driver.current_url}")
            
            # Check if we can find demo-related elements
            demo_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Demo') or contains(text(), 'GOTV')]")
            if demo_elements:
                print(f"Found {len(demo_elements)} elements containing 'Demo' or 'GOTV' text")
                for i, elem in enumerate(demo_elements[:3]):  # Print first 3
                    try:
                        print(f"  Element {i+1}: {elem.tag_name} - '{elem.text[:50]}...'")
                    except:
                        print(f"  Element {i+1}: Unable to get text")
            
            # Check page source for demo-related content
            page_source = driver.page_source
            if "data-demo-link" in page_source:
                print("✓ Found 'data-demo-link' in page source")
                # Extract demo links from page source for debugging
                import re
                demo_pattern = r'data-demo-link="([^"]*)"'
                matches = re.findall(demo_pattern, page_source)
                if matches:
                    print(f"Found demo links in source: {matches}")
            else:
                print("✗ No 'data-demo-link' found in page source")
            
            if "demo" in page_source.lower():
                print("✓ Found 'demo' text in page source")
            else:
                print("✗ No 'demo' text found in page source")
                
            return

        print(f"\nFound {len(demo_links)} demo link(s) total using selector: {successful_selector}")

        # Remove duplicates while preserving order
        unique_links = []
        seen_identifiers = set()
        
        for link in demo_links:
            # Use data-demo-link attribute or href as identifier
            identifier = link.get_attribute("data-demo-link") or link.get_attribute("href")
            if identifier and identifier not in seen_identifiers:
                unique_links.append(link)
                seen_identifiers.add(identifier)
                print(f"  Demo link: {identifier}")

        print(f"Unique demo links to download: {len(unique_links)}")

        # Download each demo
        for index, link in enumerate(unique_links, start=1):
            try:
                # Get both data-demo-link and href attributes
                demo_link = link.get_attribute("data-demo-link")
                href = link.get_attribute("href")
                
                print(f"\nAttempting to download demo {index}:")
                print(f"  data-demo-link: {demo_link}")
                print(f"  href: {href}")
                
                # For HLTV, if there's a data-demo-link, we need to construct the full URL
                if demo_link:
                    # Construct the full download URL
                    if demo_link.startswith('/'):
                        full_url = f"https://www.hltv.org{demo_link}"
                    else:
                        full_url = demo_link
                    
                    print(f"  Full download URL: {full_url}")
                    
                    # Method 1: Try clicking the original element first
                    try:
                        print(f"  Method 1: Clicking original demo button...")
                        # Scroll element into view
                        driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        time.sleep(1)
                        
                        # Try regular click first
                        link.click()
                        print(f"  ✓ Regular click successful")
                        time.sleep(10)  # Wait longer for download to start
                        
                    except Exception as click_error:
                        print(f"  ✗ Regular click failed: {click_error}")
                        
                        # Try JavaScript click
                        try:
                            print(f"  Method 2: JavaScript click...")
                            driver.execute_script("arguments[0].click();", link)
                            print(f"  ✓ JavaScript click successful")
                            time.sleep(10)
                        except Exception as js_error:
                            print(f"  ✗ JavaScript click failed: {js_error}")
                            
                            # Method 3: Direct navigation as last resort
                            try:
                                print(f"  Method 3: Direct navigation to download URL...")
                                # Open in new tab to avoid losing current page
                                driver.execute_script(f"window.open('{full_url}', '_blank');")
                                
                                # Switch to new tab
                                driver.switch_to.window(driver.window_handles[-1])
                                time.sleep(10)
                                
                                # Close the tab and switch back
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                                
                                print(f"  ✓ Direct navigation completed")
                            except Exception as nav_error:
                                print(f"  ✗ Direct navigation failed: {nav_error}")
                                continue
                
                # Check if download started by looking for new files
                current_files = set(os.listdir(download_dir)) if os.path.exists(download_dir) else set()
                time.sleep(2)
                new_files = set(os.listdir(download_dir)) if os.path.exists(download_dir) else set()
                
                if new_files - current_files:
                    print(f"  ✓ Download appears to have started (new files detected)")
                else:
                    print(f"  ? No new files detected immediately")
                
            except Exception as e:
                print(f"  ✗ Error with demo {index}: {e}")
                continue

        # Wait for downloads to complete with more thorough checking
        print("\nWaiting for downloads to complete...")
        max_wait_time = 600  # 10 minutes max wait (demos can be large)
        wait_time = 0
        check_interval = 5  # Check every 5 seconds
        
        initial_files = set(os.listdir(download_dir)) if os.path.exists(download_dir) else set()
        
        while wait_time < max_wait_time:
            try:
                current_files = set(os.listdir(download_dir)) if os.path.exists(download_dir) else set()
                
                # Check for temporary download files
                temp_files = [f for f in current_files if f.endswith(('.crdownload', '.tmp', '.part', '.download'))]
                
                # Check for new files (completed or in progress)
                new_files = current_files - initial_files
                
                if temp_files:
                    print(f"Downloads in progress: {len(temp_files)} file(s)")
                    for temp_file in temp_files:
                        temp_path = os.path.join(download_dir, temp_file)
                        if os.path.exists(temp_path):
                            size_mb = os.path.getsize(temp_path) / (1024 * 1024)
                            print(f"  - {temp_file} ({size_mb:.2f} MB)")
                elif new_files:
                    print(f"New files detected: {len(new_files)}")
                    break
                elif wait_time == 0:
                    print("No downloads detected yet, continuing to wait...")
                
                time.sleep(check_interval)
                wait_time += check_interval
                
                # Print progress every 30 seconds
                if wait_time % 30 == 0 and wait_time > 0:
                    print(f"Still waiting... ({wait_time}/{max_wait_time} seconds elapsed)")
                
            except OSError:
                time.sleep(check_interval)
                wait_time += check_interval

        if wait_time >= max_wait_time:
            print(f"Timeout reached ({max_wait_time} seconds). Stopping wait.")

        # Check final results
        try:
            final_files = os.listdir(download_dir)
            demo_files = [f for f in final_files if f.endswith(('.dem', '.zip', '.rar', '.7z', '.gz'))]
            
            print(f"\n{'='*50}")
            print(f"DOWNLOAD SUMMARY")
            print(f"{'='*50}")
            print(f"Download directory: {download_dir}")
            print(f"Total files found: {len(final_files)}")
            print(f"Demo files: {len(demo_files)}")
            print(f"{'='*50}")
            
            if demo_files:
                for file in demo_files:
                    file_path = os.path.join(download_dir, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
                    print(f"✓ {file} ({file_size:.2f} MB)")
            else:
                print("No demo files found. Possible issues:")
                print("- Downloads may still be in progress")
                print("- Files may have different extensions")
                print("- Download may have failed")
                print("\nAll files in directory:")
                for file in final_files:
                    print(f"  - {file}")
                
        except OSError as e:
            print(f"Error checking download directory: {e}")

    except TimeoutException:
        print("Page load timeout. The page might be taking too long to load.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()


if __name__ == "__main__":
    # Example usage
    download_hltv_demos()
    
    # Or with custom parameters:
    # download_hltv_demos(
    #     match_url="https://www.hltv.org/matches/2354343/wisla-krakow-vs-fnatic-iem-katowice-2022-play-in",
    #     download_dir=r"C:\path\to\your\demo\folder"
    # )