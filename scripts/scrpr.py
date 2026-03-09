from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests
import os

# 1. Setup Headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)

def get_files_from_url(url):
    """Visits a post and hunts for Excel/CSV links specifically."""
    print(f"Checking: {url}")
    driver.get(url)
    time.sleep(3) 
    
    found_links = []
    all_elements = driver.find_elements(By.TAG_NAME, "a")
    
    for link in all_elements:
        try:
            href = link.get_attribute("href")
            if not href: continue
            
            # Identify Excel or WP upload paths
            is_excel = any(ext in href.lower() for ext in ['.xls', '.xlsx', '.csv'])
            is_upload = "wp-content/uploads" in href.lower()
            
            if is_excel or is_upload:
                # Filter out non-data files
                if not any(bad in href.lower() for bad in ['.jpg', '.png', '.pdf', '.zip', '.mp4']):
                    found_links.append(href)
        except:
            continue
                
    return list(set(found_links))

try:
    # 2. Start at the Category Page
    category_url = "https://cbs.aw/wp/index.php/category/statistical-overview-of-aruba/"
    driver.get(category_url)
    time.sleep(5)

    # 3. Find the 19 posts
    post_elements = driver.find_elements(By.CSS_SELECTOR, "h2.entry-title a, a.more-link")
    post_urls = list(set([p.get_attribute("href") for p in post_elements if p.get_attribute("href")]))

    print(f"Found {len(post_urls)} posts. Starting deep scan...")

    # 4. Loop through each post and download files
    for post in post_urls:
        files = get_files_from_url(post)
        for f_url in files:
            filename = f_url.split("/")[-1]
            if os.path.exists(filename): continue
            
            print(f"   --> Downloading: {filename}")
            r = requests.get(f_url, headers={"User-Agent": "Mozilla/5.0"})
            with open(filename, 'wb') as f:
                f.write(r.content)

finally:
    print("All done.")
    driver.quit()
