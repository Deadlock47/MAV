import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
from tqdm import tqdm
import os
from pathlib import Path
from datetime import datetime
import zipfile

import os
import shutil

def clear_directory(path):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

# Usage
clear_directory('downloads')

url = "https://r18.dev/dumps"
from playwright.sync_api import sync_playwright
links_url = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    page.goto(url)

    links = page.query_selector_all("ul li a")

    for link in links:
        # print(link.get_attribute("href"))
        links_url.append(link.get_attribute("href"))

    browser.close()
print(links_url[0])
DOWNLOAD_URL = ""  # Paste your download link here
OUTPUT_DIR = "downloads"

def get_filename_from_url(url):
    """Extract filename from URL"""
    return url.split('/')[-1].split('?')[0] or "downloaded_file"

# extract filename
def download_file(url, output_path=None):
    """Download file from URL with progress tracking"""
    try:
        print("="*60)
        print("File Downloader")
        print("="*60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if not url:
            print("✗ Error: No download URL provided")
            return False
        
        print(f"Downloading from: {url}")
        print()
        
        # Add headers to avoid 403 Forbidden errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Send GET request with streaming
        response = requests.get(url, stream=True, timeout=30, headers=headers)
        response.raise_for_status()
        
        # Get total file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Determine output file path
        if output_path is None:
            filename = get_filename_from_url(url)
            output_path = os.path.join(OUTPUT_DIR, filename)
        
        print(f"Output file: {output_path}")
        
        if total_size > 0:
            print(f"File size: {total_size / (1024*1024):.2f} MB")
        print()
        
        # Download with progress bar
        downloaded = 0
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percentage = (downloaded / total_size) * 100
                        bar_length = 40
                        filled = int(bar_length * downloaded / total_size)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        print(f"\rProgress: |{bar}| {percentage:.1f}%", end="", flush=True)
        
        print()
        print("="*60)
        print("✓ Download completed successfully!")
        print(f"Saved to: {os.path.abspath(output_path)}")
        print(f"File size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Check if downloaded file is a zip and extract if requested
        # if output_path.lower().endswith('.gz'):
        #     print()
        #     response_extract = input("Extract zip file? (y/n): ").strip().lower()
        #     if response_extract == 'y':
        #         extract_zip_file(output_path)
        
        return True
        
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 403:
            print(f"✗ Error: 403 Forbidden - Access denied to this URL")
            print(f"   The server is blocking requests from this script.")
            print(f"   Try:")
            print(f"   - Adding authentication if required")
            print(f"   - Checking if the URL is still valid")
            print(f"   - Using a different download method")
        elif status_code == 404:
            print(f"✗ Error: 404 Not Found - File/URL does not exist")
        elif status_code == 401:
            print(f"✗ Error: 401 Unauthorized - Authentication required")
        else:
            print(f"✗ HTTP Error {status_code}: {e}")
        return False
    except requests.exceptions.MissingSchema:
        print("✗ Error: Invalid URL format")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Error: Connection failed. Check your internet connection.")
        return False
    except requests.exceptions.Timeout:
        print("✗ Error: Download timed out")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
download_file(links_url[0])

###################################
######       Extract Zip     ######
###################################
import zipfile
import gzip
import shutil
import os
def extract_zip_file(zip_path):
    print("="*60)
    print("Zip File Extractor")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1 — Extract .zip file
    filename = get_filename_from_url(links_url[0])
    print(filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    print(f"Output file: {output_path}")


    # Step 2 — Find .gz files
    for file in os.listdir(OUTPUT_DIR):
        if file.endswith(".gz"):

            gz_path = os.path.join(OUTPUT_DIR, file)
            sql_path = os.path.join(OUTPUT_DIR, file.replace(".gz", ""))

            # decompress gzip
            with gzip.open(gz_path, 'rb') as f_in:
                with open(sql_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            print("Extracted:", sql_path)
extract_zip_file(links_url[0])