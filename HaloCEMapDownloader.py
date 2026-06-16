import os
import sys
import zipfile
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urljoin
import shutil
import logging
import argparse
import re

# --- Constants & Configuration ---
BASE_URL = "https://www.halomaps.org/hce/"
DOWNLOADS_DIR = 'downloads'

DOWNLOAD_OPTIONS = {
    "DownloadMultiplayer": {"url": f"{BASE_URL}index.cfm?sid=10", "paginated": True, "flag": "-dm", "help": "Download multiplayer maps"},
    "DownloadMultiplayerWthAI": {"url": f"{BASE_URL}index.cfm?sid=39", "paginated": True, "flag": "-dmai", "help": "Download multiplayer maps with AI"},
    "DownloadMultiplayerModified": {"url": f"{BASE_URL}index.cfm?sid=24", "paginated": True, "flag": "-dmm", "help": "Download modified multiplayer maps"},
    "DownloadMultiplayerForMachinima": {"url": f"{BASE_URL}index.cfm?sid=29", "paginated": False, "flag": "-dmfm", "help": "Download multiplayer maps for machinima"},
    "DownloadLumoria": {"url": f"{BASE_URL}index.cfm?sid=41", "paginated": False, "flag": "-dlm", "help": "Download Lumoria maps"},
    "DownloadSingleplayerModified": {"url": f"{BASE_URL}index.cfm?sid=27", "paginated": True, "flag": "-dsm", "help": "Download modified singleplayer maps"},
    "DownloadSingleplayerCustomMaps": {"url": f"{BASE_URL}index.cfm?sid=37", "paginated": True, "flag": "-dscm", "help": "Download custom singleplayer maps"},
    "DownloadCustomUIs": {"url": f"{BASE_URL}index.cfm?sid=26", "paginated": True, "flag": "-dcui", "help": "Download custom UIs"},
    "DownloadCMTMaps": {"url": f"{BASE_URL}index.cfm?sid=35", "paginated": False, "flag": "-dcms", "help": "Download CMT Maps"},
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_downloads_folder() -> str:
    """Creates a 'downloads' folder in the current directory if it doesn't exist."""
    downloads_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), DOWNLOADS_DIR)
    os.makedirs(downloads_path, exist_ok=True)
    logging.info(f"Downloads folder path: {downloads_path}")
    return downloads_path

def download_file(url: str, post_data: dict, filename: str, downloads_directory: str) -> str | None:
    """Downloads a file from the given URL using the provided POST data."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.post(url, data=post_data, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        file_path = os.path.join(downloads_directory, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"Downloaded file: {file_path}")
        return file_path
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading {url}: {e}")
        return None

def get_download_info(browser: webdriver.Chrome, url: str) -> tuple[str | None, dict | None]:
    """Retrieves download information (filename and POST data) from a map detail page."""
    browser.get(url)
    try:
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.NAME, 'fid')))
    except TimeoutException:
        logging.error("Timed out waiting for the download form.")
        return None, None

    soup = BeautifulSoup(browser.page_source, "html.parser")
    fid, action, hash_val = soup.find('input', {'name': 'fid'}), soup.find('input', {'name': 'action'}), soup.find('input', {'name': 'hash'})
    if not (fid and action and hash_val):
        logging.error("Target form not found on the details page.")
        return None, None

    post_data = {'fid': fid['value'], 'action': action['value'], 'hash': hash_val['value']}
    filename = "downloaded_file.zip"
    
    h1 = soup.find('h1')
    if h1:
        filename = h1.text.replace("Halo Custom Edition Map:", "").strip().replace(" ", "") + ".zip"
        filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    else:
        logging.warning("h1 element not found. Trying Content-Disposition fallback.")
        try:
            WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, "//meta[@http-equiv='Content-Disposition']")))
            meta = browser.execute_script("return document.querySelector('meta[http-equiv=\"Content-Disposition\"]').content")
            if meta:
                filename = re.sub(r'[\\/*?:"<>|]', "", meta.split("filename=")[-1].strip('"'))
        except Exception as e:
            logging.warning(f"Could not extract fallback filename: {e}")

    return filename, post_data

def scrape_filelinks(browser: webdriver.Chrome, base_url: str, downloads_directory: str, paginated: bool = False):
    """Scrapes file links from a given URL (supporting pagination) and initiates downloads."""
    urls = [f"{base_url}&sort=1&Start={i}" if i > 0 else base_url for i in range(0, 401, 30)] if paginated else [base_url]
    
    for url in urls:
        browser.get(url)
        try:
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'image-fade')))
        except TimeoutException:
            logging.error(f"Timed out waiting for file links on {url}")
            continue

        soup = BeautifulSoup(browser.page_source, "html.parser")
        for link in soup.find_all('a', class_='image-fade'):
            href = link.get('href')
            if href:
                complete_url = urljoin(BASE_URL, href)
                logging.info(f"Found link: {complete_url}")
                filename, post_data = get_download_info(browser, complete_url)
                if filename and post_data:
                    download_file(f'{BASE_URL}detail.cfm', post_data, filename, downloads_directory)

def install_downloaded_maps(install_dir: str, downloads_directory: str):
    """Extracts .map files from zip archives and moves existing/extracted .map files to Halo maps directory."""
    maps_dir = os.path.join(install_dir, 'maps')
    if not (os.path.exists(os.path.join(install_dir, 'halo.exe')) and os.path.exists(maps_dir)):
        logging.error("Halo installation or maps directory not found.")
        return

    # Process all zips and maps in the downloads directory
    for root, _, files in os.walk(downloads_directory):
        for file in files:
            file_path = os.path.join(root, file)
            dest_path = os.path.join(maps_dir, file)
            
            if file.endswith('.map'):
                if file.lower() == 'ui.map' and os.path.exists(dest_path):
                    logging.info("ui.map already exists. Skipping.")
                    continue
                if os.path.exists(dest_path):
                    logging.info(f"File {file} already exists. Skipping.")
                    continue
                try:
                    shutil.move(file_path, dest_path)
                    logging.info(f"Moved {file} to {dest_path}")
                except OSError as e:
                    logging.error(f"Error moving {file}: {e}")

            elif file.endswith('.zip'):
                try:
                    with zipfile.ZipFile(file_path, 'r') as z:
                        for member in z.namelist():
                            if member.endswith('.map') and not member.endswith('/'):
                                filename = os.path.basename(member)
                                target_dest = os.path.join(maps_dir, filename)
                                
                                if filename.lower() == 'ui.map' and os.path.exists(target_dest):
                                    logging.info("ui.map already exists. Skipping.")
                                    continue
                                if os.path.exists(target_dest):
                                    logging.info(f"File {filename} already exists. Skipping.")
                                    continue
                                try:
                                    with z.open(member) as source, open(target_dest, 'wb') as target:
                                        shutil.copyfileobj(source, target)
                                    logging.info(f"Extracted and installed {filename} to {target_dest}")
                                except Exception as e:
                                    logging.error(f"Error extracting {filename} from zip: {e}")
                except zipfile.BadZipFile:
                    logging.error(f"Bad zip file: {file_path}")
                except Exception as e:
                    logging.error(f"Error reading zip {file_path}: {e}")
                     
    # Clean up all files and directories in downloads_directory
    for item in os.listdir(downloads_directory):
        item_path = os.path.join(downloads_directory, item)
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            logging.error(f"Failed to delete {item_path}: {e}")

def setup_browser() -> webdriver.Chrome:
    """Sets up and returns a headless Chrome webdriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def process_downloads(browser: webdriver.Chrome, downloads_directory: str, options: dict):
    """Processes the selected download options."""
    for option, details in options.items():
        if details["selected"]:
            logging.info(f"Starting {option} download...")
            if option == "DownloadLumoria":
                logging.warning("Lumoria maps may require manual installation of sound DLLs.")
            scrape_filelinks(browser, details["url"], downloads_directory, details["paginated"])

def main():
    parser = argparse.ArgumentParser(description="Download and install Halo maps from halomaps.org.")
    parser.add_argument("--HaloInstallDir", help="Specify the Halo installation directory")

    for name, config in DOWNLOAD_OPTIONS.items():
        parser.add_argument(config["flag"], f"--{name}", action="store_true", help=config["help"])
    args = parser.parse_args()

    if args.DownloadCMTMaps and args.HaloInstallDir:
        logging.error("Error: --HaloInstallDir cannot be used with -dcms/--DownloadCMTMaps.")
        logging.error("CMT maps require manual installation.")
        sys.exit(1)

    downloads_directory = create_downloads_folder()
    browser = setup_browser()

    selected_options = {
        name: {**config, "selected": getattr(args, name, False)}
        for name, config in DOWNLOAD_OPTIONS.items()
    }

    try:
        if any(option["selected"] for option in selected_options.values()):
            process_downloads(browser, downloads_directory, selected_options)

        if args.HaloInstallDir:
            if os.path.exists(args.HaloInstallDir):
                install_downloaded_maps(args.HaloInstallDir, downloads_directory)
            else:
                logging.error(f"Error: Directory {args.HaloInstallDir} does not exist.")
                sys.exit(1)
    finally:
        browser.quit()

if __name__ == "__main__":
    main()