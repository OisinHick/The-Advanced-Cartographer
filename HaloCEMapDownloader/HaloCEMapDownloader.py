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
from webdriver_manager.chrome import ChromeDriverManager  # Import webdriver_manager


# --- Constants ---
BASE_URL = "https://www.halomaps.org/hce/"
DOWNLOADS_DIR = 'downloads'

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_downloads_folder():
    downloads_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), DOWNLOADS_DIR)
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
        logging.info(f"Created 'downloads' folder at: {downloads_path}")
    else:
        logging.info(f"'downloads' folder already exists at: {downloads_path}")
    return downloads_path

def download_file(url, post_data, filename, downloads_directory):
    try:
        response = requests.post(url, data=post_data, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        file_path = os.path.join(downloads_directory, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"Downloaded file: {file_path}")
        return file_path  # Return the path for later use (unzipping)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading {url}: {e}")
        return None


def get_download_info(browser, url):
    browser.get(url)
    try:
        # Explicit wait for the presence of the 'fid' input element
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

        # --- Get filename from <h1> using XPath ---
        filename = "downloaded_file.zip"  # Default filename
        try:
            # Use XPath to find the h1 element
            h1_element = browser.find_element(By.XPATH, "/html/body/section[1]/div/div/div[2]/div/div/h1")
            filename_text = h1_element.text
            
            #Basic processing to remove unwanted text, and add extension
            filename = filename_text.replace("Halo Custom Edition Map:", "").replace(" ", "").strip() + ".zip"
        
        except Exception as e:
            logging.warning(f"Could not extract filename from <h1>: {e}. Using default filename.")


        # --- Fallback: Get from Content-Disposition (if XPath fails) ---
        if filename == "downloaded_file.zip":  # Check if default is still used
            try:
                content_disposition = browser.execute_script(
                    "return document.querySelector('meta[http-equiv=\"Content-Disposition\"]').content"
                )
                if content_disposition:
                    filename = content_disposition.split("filename=")[-1].strip('"')
            except Exception as e:
                logging.warning(f"Could not extract filename from Content-Disposition: {e}")
        return filename, post_data
    else:
        logging.error("Target form not found.")
        return None, None

def scrape_filelinks(browser, url, downloads_directory):
    browser.get(url)
    try:
        # Wait for at least one element with the class 'image-fade' to be present
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
                download_file(f'{BASE_URL}detail.cfm', post_data, filename, downloads_directory)  # Corrected URL



def unzip_downloads(install_dir, downloads_directory):
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


def move_map_files(install_dir, downloads_directory):
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
                        continue  # Skip to the next file

                if os.path.exists(destination_path):
                    logging.info(f"File {file} already exists. Skipping.")
                    continue

                try:
                    shutil.move(map_file_path, destination_path)
                    logging.info(f"Moved {file} to {destination_path}")
                     # Delete the file AFTER successful move
                    os.remove(map_file_path)
                except OSError as e:
                    logging.error(f"Error moving {file}: {e}")


    # Empty the downloads directory after moving the files
    for file in os.listdir(downloads_directory):
        file_path = os.path.join(downloads_directory, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(f"Failed to delete {file_path}. Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download and install Halo maps from halomaps.org.")
    parser.add_argument("--HaloInstallDir", help="Specify the Halo installation directory")
    parser.add_argument("-dm", "--DownloadMultiplayer", action="store_true", help="Download multiplayer maps")
    parser.add_argument("-dmai", "--DownloadMultiplayerWthAI", action="store_true", help="Download multiplayer maps with AI")
    parser.add_argument("-dmm", "--DownloadMultiplayerModified", action="store_true", help="Download modified multiplayer maps")
    parser.add_argument("-dmfm", "--DownloadMultiplayerForMachinima", action="store_true", help="Download multiplayer maps for machinima")
    parser.add_argument("-dlm", "--DownloadLumoria", action="store_true", help="Download Lumoria maps")
    parser.add_argument("-dsm", "--DownloadSingleplayerModified", action="store_true", help="Download modified singleplayer maps")
    parser.add_argument("-dscm", "--DownloadSingleplayerCustomMaps", action="store_true", help="Download custom singleplayer maps")
    args = parser.parse_args()

    downloads_directory = create_downloads_folder()

    # --- Selenium Setup (using webdriver_manager) ---
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode
    # Use webdriver_manager to handle ChromeDriver
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=chrome_options)


    try:
        if args.HaloInstallDir:
            if os.path.exists(args.HaloInstallDir):
                unzip_downloads(args.HaloInstallDir, downloads_directory)
                move_map_files(args.HaloInstallDir, downloads_directory)
            else:
                logging.error(f"Error: Directory {args.HaloInstallDir} does not exist.")
                sys.exit(1)

        if args.DownloadMultiplayer:
            logging.info("Starting multiplayer map download...")
            scrape_filelinks(browser, "https://www.halomaps.org/hce/index.cfm?sid=10", downloads_directory)
            for i in range(0, 400):
                start_value = 31 + i * 30
                url_page_one = f"https://www.halomaps.org/hce/index.cfm?sid=10&sort=1&Start={start_value}"
                scrape_filelinks(browser, url_page_one, downloads_directory)

        if args.DownloadMultiplayerWthAI:
            logging.info("Starting multiplayer map with AI download...")
            scrape_filelinks(browser, "https://www.halomaps.org/hce/index.cfm?sid=39", downloads_directory)
            for i in range(0, 400):
                start_value = 31 + i * 30
                url_page_one = f"https://www.halomaps.org/hce/index.cfm?sid=39&sort=1&Start={start_value}"
                scrape_filelinks(browser, url_page_one, downloads_directory)

        if args.DownloadMultiplayerModified:
            logging.info("Starting modified multiplayer map download...")
            scrape_filelinks(browser, "https://www.halomaps.org/hce/index.cfm?sid=24", downloads_directory)
            for i in range(0, 400):
                start_value = 31 + i * 30
                url_page_one = f"https://www.halomaps.org/hce/index.cfm?sid=24&sort=1&Start={start_value}"
                scrape_filelinks(browser, url_page_one, downloads_directory)

        if args.DownloadMultiplayerForMachinima:
            logging.info("Starting machinima multiplayer map download...")
            scrape_filelinks(browser, "https://www.halomaps.org/hce/index.cfm?sid=29", downloads_directory)

        if args.DownloadLumoria:
            logging.info("Starting Lumoria map download...")
            filename, post_data = get_download_info(browser, "https://www.halomaps.org/hce/detail.cfm?fid=6507")
            if filename and post_data:
                download_file(f'{BASE_URL}detail.cfm', post_data, filename, downloads_directory)

        if args.DownloadSingleplayerModified:
            logging.info("Starting modified singleplayer map download...")
            scrape_filelinks(browser, "https://www.halomaps.org/hce/index.cfm?sid=27", downloads_directory)
            for i in range(0, 400):
                start_value = 31 + i * 30
                url_page_one = f"https://www.halomaps.org/hce/index.cfm?sid=27&sort=1&Start={start_value}"
                scrape_filelinks(browser, url_page_one, downloads_directory)

        if args.DownloadSingleplayerCustomMaps:
            logging.info("Starting custom singleplayer map download...")
            scrape_filelinks(browser, "https://www.halomaps.org/hce/index.cfm?sid=37", downloads_directory)
            for i in range(0, 400):
                start_value = 31 + i * 30
                url_page_one = f"https://www.halomaps.org/hce/index.cfm?sid=37&sort=1&Start={start_value}"
                scrape_filelinks(browser, url_page_one, downloads_directory)

    finally:
        browser.quit()  # Ensure the browser is closed even if errors occur


if __name__ == "__main__":
    main()