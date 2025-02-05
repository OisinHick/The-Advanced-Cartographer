import os
import sys
import zipfile
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import shutil
import logging
import argparse
from webdriver_manager.chrome import ChromeDriverManager
import re

# --- Constants ---
BASE_URL = "https://www.halomaps.org/hce/"
DOWNLOADS_DIR = 'downloads'

# --- Configuration ---
# Dictionary mapping download options to their corresponding URLs and pagination status
DOWNLOAD_OPTIONS = {
    "DownloadMultiplayer": {"url": "https://www.halomaps.org/hce/index.cfm?sid=10", "paginated": True},
    "DownloadMultiplayerWthAI": {"url": "https://www.halomaps.org/hce/index.cfm?sid=39", "paginated": True},
    "DownloadMultiplayerModified": {"url": "https://www.halomaps.org/hce/index.cfm?sid=24", "paginated": True},
    "DownloadMultiplayerForMachinima": {"url": "https://www.halomaps.org/hce/index.cfm?sid=29", "paginated": False},
    "DownloadLumoria": {"url": "https://www.halomaps.org/hce/index.cfm?sid=41", "paginated": False},
    "DownloadSingleplayerModified": {"url": "https://www.halomaps.org/hce/index.cfm?sid=27", "paginated": True},
    "DownloadSingleplayerCustomMaps": {"url": "https://www.halomaps.org/hce/index.cfm?sid=37", "paginated": True},
    "DownloadCustomUIs": {"url": "https://www.halomaps.org/hce/index.cfm?sid=26", "paginated": True},
    "DownloadCMTMaps": {"url": "https://www.halomaps.org/hce/index.cfm?sid=35", "paginated": False},
}

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_downloads_folder() -> str:
    """Creates a 'downloads' folder in the current directory if it doesn't exist."""
    downloads_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), DOWNLOADS_DIR)
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
        logging.info(f"Created 'downloads' folder at: {downloads_path}")
    else:
        logging.info(f"'downloads' folder already exists at: {downloads_path}")
    return downloads_path

def download_file(url: str, post_data: dict, filename: str, downloads_directory: str) -> str | None:
    """Downloads a file from the given URL using the provided POST data."""
    try:
        response = requests.post(url, data=post_data, stream=True)
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
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, 'fid'))
        )
    except TimeoutError:
        logging.error("Timed out waiting for the form.")
        return None, None

    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")

    fid = soup.find('input', {'name': 'fid'})
    action = soup.find('input', {'name': 'action'})
    hash_value = soup.find('input', {'name': 'hash'})

    if fid and action and hash_value:
        post_data = {
            'fid': fid['value'],
            'action': action['value'],
            'hash': hash_value['value']
        }

        filename = "downloaded_file.zip"
        try:
            h1_element = browser.find_element(By.XPATH, "/html/body/section[1]/div/div/div[2]/div/div/h1")
            filename_text = h1_element.text
            match = re.search(r"(.+)", filename_text)
            if match:
                filename = match.group(1).replace("Halo Custom Edition Map:", "").strip().replace(" ", "") + ".zip"
                filename = re.sub(r'[\\/*?:"<>|]', "", filename)
            else:
                logging.warning("Could not parse filename from h1 text. Using default.")
        except Exception as e:
            logging.warning(f"Could not extract filename from <h1>: {e}. Using default filename.")

        if filename == "downloaded_file.zip":
            try:
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//meta[@http-equiv='Content-Disposition']"))
                )
                content_disposition = browser.execute_script(
                    "return document.querySelector('meta[http-equiv=\"Content-Disposition\"]').content"
                )
                if content_disposition:
                    filename = content_disposition.split("filename=")[-1].strip('"')
                    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
            except Exception as e:
                logging.warning(f"Could not extract filename from Content-Disposition: {e}")
        return filename, post_data
    else:
        logging.error("Target form not found.")
        return None, None

def scrape_filelinks(browser: webdriver.Chrome, url: str, downloads_directory: str, paginated: bool = False):
    """Scrapes file links from a given URL and initiates downloads."""
    if paginated:
        for i in range(0, 401, 30):  # Corrected loop for pagination
            page_url = f"{url}&sort=1&Start={i}" if i > 0 else url #Simplified URL building.
            _scrape_page(browser, page_url, downloads_directory)
    else:
        _scrape_page(browser, url, downloads_directory)


def _scrape_page(browser: webdriver.Chrome, url: str, downloads_directory: str):
    """Helper function to scrape a single page (used for both paginated and non-paginated)."""
    browser.get(url)
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'image-fade'))
        )
    except TimeoutError:
        logging.error(f"Timed out waiting for file links on {url}")
        return

    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")

    filelink_elements = soup.find_all('a', class_='image-fade')
    for filelink_element in filelink_elements:
        href_value = filelink_element.get('href')
        if href_value:
            complete_url = urljoin(BASE_URL, href_value)
            logging.info(f"Found link: {complete_url}")
            filename, post_data = get_download_info(browser, complete_url)
            if filename and post_data:
                download_file(f'{BASE_URL}detail.cfm', post_data, filename, downloads_directory)


def unzip_downloads(install_dir: str, downloads_directory: str):
    """Unzips downloaded files into the downloads directory."""
    halo_exe_path = os.path.join(install_dir, 'halo.exe')
    maps_dir_path = os.path.join(install_dir, 'maps')

    if not (os.path.exists(halo_exe_path) and os.path.exists(maps_dir_path)):
        logging.error("Halo installation or maps directory not found.")
        return

    for root, _, files in os.walk(downloads_directory):
        for file in files:
            if file.endswith('.zip'):
                zip_file_path = os.path.join(root, file)
                try:
                    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                        zip_ref.extractall(downloads_directory)
                    logging.info(f"Extracted: {zip_file_path}")
                except zipfile.BadZipFile:
                    logging.error(f"Bad zip file: {zip_file_path}")
                except Exception as e:
                    logging.error(f"Error extracting {zip_file_path}: {e}")


def move_map_files(install_dir: str, downloads_directory: str):
    """Moves .map files from the downloads directory to the Halo maps directory."""
    maps_dir_path = os.path.join(install_dir, 'maps')

    if not os.path.exists(maps_dir_path):
        logging.error(f"Maps directory not found: {maps_dir_path}")
        return

    for root, _, files in os.walk(downloads_directory):
        for file in files:
            if file.endswith('.map'):
                map_file_path = os.path.join(root, file)
                destination_path = os.path.join(maps_dir_path, file)

                if file.lower() == 'ui.map':
                    if os.path.exists(destination_path):
                        logging.info(f"ui.map already exists. Skipping.")
                        continue

                if os.path.exists(destination_path):
                    logging.info(f"File {file} already exists. Skipping.")
                    continue

                try:
                    shutil.move(map_file_path, destination_path)
                    logging.info(f"Moved {file} to {destination_path}")
                    os.remove(map_file_path)  # Delete after successful move
                except OSError as e:
                    logging.error(f"Error moving {file}: {e}")

    # Clean up remaining files (not subdirectories) in downloads directory
    for file in os.listdir(downloads_directory):
        file_path = os.path.join(downloads_directory, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            logging.error(f"Failed to delete {file_path}. Error: {e}")

def setup_browser() -> webdriver.Chrome:
    """Sets up and returns a headless Chrome webdriver instance."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def process_downloads(browser: webdriver.Chrome, downloads_directory: str, options: dict):
    """Processes the selected download options."""
    for option, details in options.items():
        if details["selected"]:
            logging.info(f"Starting {option} download...")
            scrape_filelinks(browser, details["url"], downloads_directory, details["paginated"])


def main():
    parser = argparse.ArgumentParser(description="Download and install Halo maps from halomaps.org.")
    parser.add_argument("--HaloInstallDir", help="Specify the Halo installation directory")
    # Create a group for mutually exclusive options (either specify a dir or download, not both)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-dm", "--DownloadMultiplayer", action="store_true", help="Download multiplayer maps")
    group.add_argument("-dmai", "--DownloadMultiplayerWthAI", action="store_true", help="Download multiplayer maps with AI")
    group.add_argument("-dmm", "--DownloadMultiplayerModified", action="store_true", help="Download modified multiplayer maps")
    group.add_argument("-dmfm", "--DownloadMultiplayerForMachinima", action="store_true", help="Download multiplayer maps for machinima")
    group.add_argument("-dlm", "--DownloadLumoria", action="store_true", help="Download Lumoria maps")
    group.add_argument("-dsm", "--DownloadSingleplayerModified", action="store_true", help="Download modified singleplayer maps")
    group.add_argument("-dscm", "--DownloadSingleplayerCustomMaps", action="store_true", help="Download custom singleplayer maps")
    group.add_argument("-dcui", "--DownloadCustomUIs", action="store_true", help="Download custom UIs")
    group.add_argument("-dcms", "--DownloadCMTMaps", action="store_true", help="Download CMT Maps")

    args = parser.parse_args()

    downloads_directory = create_downloads_folder()

    # Set up browser
    browser = setup_browser()

    # Create a dictionary to hold selected download options
    selected_options = {
        option: {"url": details["url"], "paginated": details["paginated"], "selected": False}
        for option, details in DOWNLOAD_OPTIONS.items()
    }

    # Update selected options based on command-line arguments
    for arg, value in vars(args).items():
        if arg in selected_options and value:
            selected_options[arg]["selected"] = True

    try:
        if args.HaloInstallDir:
            if os.path.exists(args.HaloInstallDir):
                unzip_downloads(args.HaloInstallDir, downloads_directory)
                move_map_files(args.HaloInstallDir, downloads_directory)
            else:
                logging.error(f"Error: Directory {args.HaloInstallDir} does not exist.")
                sys.exit(1)
        else:  # Only process downloads if no install dir is specified
            process_downloads(browser, downloads_directory, selected_options)

    finally:
        browser.quit()



if __name__ == "__main__":
    main()