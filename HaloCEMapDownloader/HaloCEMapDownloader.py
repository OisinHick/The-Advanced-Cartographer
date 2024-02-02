import os
import getopt
import sys
import zipfile
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
import shutil

# Get the current working directory
current_directory = os.path.dirname(os.path.realpath(__file__))
downloads_directory = os.path.join(current_directory, 'downloads')

# Function to scrape file links
def scrape_filelinks(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    
    # Construct the local path for chromedriver.exe
    chromedriver_path = os.path.join(current_directory, 'chromedriver.exe')
    
    cService = webdriver.ChromeService(executable_path=chromedriver_path)
    browser = webdriver.Chrome(service=cService, options=chrome_options)

    browser.get(url)
    browser.implicitly_wait(320)
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")

    filelink_elements = soup.find_all('a', class_='image-fade')
    for filelink_element in filelink_elements:
        href_value = filelink_element.get('href')
        if href_value:
            complete_url = urljoin("https://www.halomaps.org/hce/", href_value)
            print(complete_url)
            scrape_filelinks_download(complete_url)

    browser.quit()

# Function to scrape file links and send a POST request
def scrape_filelinks_download(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument(f'--download.default_directory={downloads_directory}')
    
    # Construct the local path for chromedriver.exe
    chromedriver_path = os.path.join(current_directory, 'chromedriver.exe')
    
    cService = webdriver.ChromeService(executable_path=chromedriver_path)
    browser = webdriver.Chrome(service=cService, options=chrome_options)

    browser.get(url)
    browser.implicitly_wait(320)
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Extracting values
    fid = soup.find('input', {'name': 'fid'})['value']
    action = soup.find('input', {'name': 'action'})['value']
    hash_value = soup.find('input', {'name': 'hash'})['value']

    if fid and action and hash_value:
        print("Found the target form:")
        print(fid, action, hash_value)

        # Sending POST request
        post_data = {
            'fid': fid,
            'action': action,
            'hash': hash_value
        }
        post_url = 'https://www.halomaps.org/hce/detail.cfm'
        response = requests.post(post_url, data=post_data)

        # Handle the response as needed
        if response.status_code == 200:
            # Extracting the filename from the content-disposition header, if available
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                filename = content_disposition.split("filename=")[-1]
            else:
                filename = "downloaded_file.zip"

            # Save the response content to a file
            file_path = os.path.join(downloads_directory, filename)
            with open(file_path, 'wb') as file:
                file.write(response.content)

            print(f"Downloaded file: {file_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    else:
        print("Target form not found.")

    browser.quit()

# Function to unzip files in the downloads folder
def unzip_downloads(install_dir):
    halo_exe_path = os.path.join(install_dir, 'halo.exe')
    maps_dir_path = os.path.join(install_dir, 'maps')

    if os.path.exists(halo_exe_path) and os.path.exists(maps_dir_path):
        for root, dirs, files in os.walk(downloads_directory):
            for file in files:
                if file.endswith('.zip'):
                    zip_file_path = os.path.join(root, file)
                    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                        zip_ref.extractall(downloads_directory)

# Function to move .map files to the installation's map folder
def move_map_files(install_dir):
    maps_dir_path = os.path.join(install_dir, 'maps')
    ui_map_name = 'ui.map'

    if os.path.exists(maps_dir_path):
        ui_map_destination_path = os.path.join(maps_dir_path, ui_map_name)

        # Check if ui.map already exists in the destination
        ui_map_already_exists = os.path.exists(ui_map_destination_path)

        for root, dirs, files in os.walk(downloads_directory):
            for file in files:
                if file.endswith('.map'):
                    map_file_path = os.path.join(root, file)
                    destination_path = os.path.join(maps_dir_path, file)

                    # Check if the file is a ui.map file
                    if file.lower() == ui_map_name.lower():
                        if not ui_map_already_exists:
                            shutil.move(map_file_path, ui_map_destination_path)
                            print(f"Moved file: {file} to {ui_map_destination_path}")
                        else:
                            print(f"{ui_map_name} already exists in {maps_dir_path}. Keeping the original.")
                        break  # Skip other files if ui.map is already moved or exists
                    else:
                        # Check if the file already exists in the destination
                        if not os.path.exists(destination_path):
                            shutil.move(map_file_path, destination_path)
                            print(f"Moved file: {file} to {maps_dir_path}")
                        else:
                            print(f"File {file} already exists in {maps_dir_path}. Skipping.")

        # Empty the downloads directory after moving the files
        for file in os.listdir(downloads_directory):
            file_path = os.path.join(downloads_directory, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Error: {e}")

def main():
    argumentList = sys.argv[1:]

    # Options
    options = "hmo:"
    # Long options
    long_options = ["Help", "HaloInstallDir=", "DownloadMultiplayer", "DownloadMultiplayerWthAI", "DownloadMultiplayerModified", "DownloadMultiplayerForMachinima", "DownloadLumoria", "DownloadSingleplayerModified", "DownloadSingleplayerCustomMaps"]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)

        # checking each argument
        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h", "--Help"):
                print("Displaying Help")
                print("Options:")
                print("    -h, --Help: Display this help menu")
                print("    --HaloInstallDir=<value>: Specify the Halo installation directory which will copy maps downloaded to there")
                print("    -dm, --DownloadMultiplayer: Start the download process for multiplayer maps")
                print("    -dlm, --DownloadLumoria: Start the download process for the Lumoria maps")
                print("    -dmai, --DownloadMultiplayerWthAI: Start the download process for multiplayer maps which have AI")
                print("    -dmm, --DownloadMultiplayerModified: Start the download process for multiplayer maps which are modified")
                print("    -dmfm, --DownloadMultiplayerForMachinima: Start the download process for multiplayer maps which are used in machinimas")
                print("    -dsm, --DownloadSingleplayerModified: Start the download process for singleplayer maps which are modified")
                print("    -dscm, --DownloadSingleplayerCustomMaps: Start the download process for singleplayer maps which are custom")




            elif currentArgument in ("--HaloInstallDir"):
                # Error handling implemented here to check that param is either true or false
                print(("Moving files to (% s)") % (currentValue))
                if os.path.exists(currentValue):
                    unzip_downloads(currentValue)
                    move_map_files(currentValue)
                else:
                    print(f"Error: Directory {currentValue} does not exist.")

            elif currentArgument in ("-dm", "--DownloadMultiplayer"):
                print("Download Started")

                # Run the scraping function for the first URL
                scrape_filelinks("https://www.halomaps.org/hce/index.cfm?sid=10")

                # Run the scraping function for the second URL with Start parameter incremented by 30
                for i in range(0, 400):  # Adjust the range based on how many times you want to increment Start
                    start_value = 31 + i * 30
                    url_page_one = f"https://www.halomaps.org/hce/index.cfm?sid=10&sort=1&Start={start_value}"
                    scrape_filelinks(url_page_one)
            
            elif currentArgument in ("-dmai", "--DownloadMultiplayerWthAI"):
                print("Download Started")

                # Run the scraping function for the first URL
                scrape_filelinks("https://www.halomaps.org/hce/index.cfm?sid=39")

                # Run the scraping function for the second URL with Start parameter incremented by 30
                for i in range(0, 400):  # Adjust the range based on how many times you want to increment Start
                    start_value = 31 + i * 30
                    url_page_one = f"https://www.halomaps.org/hce/index.cfm?sid=39&sort=1&Start={start_value}"
                    scrape_filelinks(url_page_one)

            elif currentArgument in ("-dmm", "--DownloadMultiplayerModified"):
                print("Download Started")

                # Run the scraping function for the first URL
                scrape_filelinks("https://www.halomaps.org/hce/index.cfm?sid=24")

                # Run the scraping function for the second URL with Start parameter incremented by 30
                for i in range(0, 400):  # Adjust the range based on how many times you want to increment Start
                    start_value = 31 + i * 30
                    url_page_one = f"https://www.halomaps.org/hce/index.cfm?sid=24&sort=1&Start={start_value}"
                    scrape_filelinks(url_page_one)

            elif currentArgument in ("-dmfm", "--DownloadMultiplayerForMachinima"):
                print("Download Started")

                # Run the scraping function for the first URL
                scrape_filelinks("https://www.halomaps.org/hce/index.cfm?sid=29")

            elif currentArgument in ("-dlm", "--DownloadLumoria"):
                print("Download Started")

                # Run the scraping function for the lumoria URL here
                scrape_filelinks_download("https://www.halomaps.org/hce/detail.cfm?fid=6507")
            
            elif currentArgument in ("-dsm", "--DownloadSingleplayerModified"):
                print("Download Started")

                # Run the scraping function for the first URL
                scrape_filelinks("https://www.halomaps.org/hce/index.cfm?sid=27")

                # Run the scraping function for the second URL with Start parameter incremented by 30
                for i in range(0, 400):  # Adjust the range based on how many times you want to increment Start
                    start_value = 31 + i * 30
                    url_page_one = f"https://www.halomaps.org/hce/index.cfm?sid=27&sort=1&Start={start_value}"
                    scrape_filelinks(url_page_one)
            
            elif currentArgument in ("-dscm", "--DownloadSingleplayerCustomMaps"):
                print("Download Started")

                # Run the scraping function for the first URL
                scrape_filelinks("https://www.halomaps.org/hce/index.cfm?sid=37")

                # Run the scraping function for the second URL with Start parameter incremented by 30
                for i in range(0, 400):  # Adjust the range based on how many times you want to increment Start
                    start_value = 31 + i * 30
                    url_page_one = f"https://www.halomaps.org/hce/index.cfm?sid=27&sort=1&Start={start_value}"
                    scrape_filelinks(url_page_one)

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))


if __name__ == "__main__":
    main()
