import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver(headless=False):
    """Setup and return Chrome WebDriver."""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
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

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def read_urls(filename="all_match_urls.txt"):
    """Read URLs from file."""
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except:
        return []

def extract_demo_link(driver, url):
    """Extract demo links from current page."""
    # demo_links = []
    
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, "[data-demo-link]")
        
        for element in elements:
            demo_link = element.get_attribute("data-demo-link")
            # if demo_link:
            #     full_url = f"https://www.hltv.org{demo_link}" if demo_link.startswith('/') else demo_link
            #     demo_links.append({
            #         'source_url': url,
            #         'demo_link': demo_link,
            #         'full_demo_url': full_url
            #     })
    except:
        pass
    
    # return demo_links
    return demo_link

def handle_cookie_banner(driver):
    """Handle cookie consent banner if present."""
    try:
        # Wait for cookie banner and click decline button
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonDecline"))
        )
        cookie_button.click()
        time.sleep(1)  # Brief pause after clicking
    except:
        # Cookie banner not present or already handled
        pass

def process_url(driver, url):
    """Process single URL and return demo links."""
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Handle cookie consent banner
        handle_cookie_banner(driver)

        # driver.close()
        
        return extract_demo_link(driver, url)
    except:
        return "None"

def save_demo_links(demo_links, filename="all_match_download_url.txt"):
    """Save demo links to file."""
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for demo_data in demo_links:
                # file.write(f"Source: {demo_data['source_url']}\n")
                # file.write(f"Demo Link: {demo_data['demo_link']}\n")
                # file.write(f"Full URL: {demo_data['full_demo_url']}\n")
                # file.write("-" * 80 + "\n")
                file.write(f"https://www.hltv.org{demo_data}\n")
    except:
        pass

def process_single_url_with_fresh_driver(url, headless=False):
    """Process single URL with a fresh driver instance."""
    driver = None
    try:
        # Create fresh driver for this URL
        driver = setup_driver(headless)
        
        # Navigate to URL
        driver.get(url)
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Handle cookie consent banner
        handle_cookie_banner(driver)
        
        # Extract demo links
        demo_link = extract_demo_link(driver, url)
        print(demo_link)
        
        return demo_link
        
    except:
        return []
    finally:
        # Always close driver
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    """Main function."""
    headless_input = input("Run in headless mode? (y/n) [default: n]: ").strip().lower()
    headless = headless_input in ['y', 'yes']
    
    wait_input = input("Wait time between URLs (seconds) [default: 3]: ").strip()
    try:
        wait_time = int(wait_input) if wait_input else 3
    except ValueError:
        wait_time = 3
    
    interactive_input = input("Interactive mode? (y/n) [default: n]: ").strip().lower()
    interactive = interactive_input in ['y', 'yes']
    
    filename = "all_match_urls.txt"
    
    # Read URLs
    urls = read_urls(filename)
    if not urls:
        print("No URLs found.")
        return
    
    # Setup driver
    driver = setup_driver(headless)
    all_demo_links = []
    
    try:
        for i, url in enumerate(urls, 1):
            
            if i < 5:
                # # Process URL
                # demo_link = process_url(driver, url)
                # all_demo_links.append(demo_link)

                # Process URL with fresh driver
                demo_links = process_single_url_with_fresh_driver(url, headless)
                all_demo_links.append(demo_links)
                
                if interactive:
                    user_input = input(f"\nPress Enter to continue (or 'q' to quit): ").strip().lower()
                    if user_input == 'q':
                        break
                
                if i < len(urls):
                    time.sleep(wait_time)

            else: 
                break

        
        print("works")
        # Output results
        if all_demo_links:
            # print(all_demo_links)
            print(f"Extracted {len(all_demo_links)} demo links:")
            # for i, demo_data in enumerate(all_demo_links, 1):
            #     print(f"{i}. {demo_data['full_demo_url']}")
            
            save_demo_links(all_demo_links)
            print(f"Demo links saved to 'all_match_download_url.txt'")
        else:
            print("No demo links found.")
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()