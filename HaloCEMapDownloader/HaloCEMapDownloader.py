import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin

# Function to scrape file links
def scrape_filelinks(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    cService = webdriver.ChromeService(executable_path='D:\\Github\\Halo-CE-Map-Downloads-System\\HaloCEMapDownloader\\chromedriver.exe')
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
    chrome_options.add_argument(f'--download.default_directory=D:\Github\Halo-CE-Map-Downloads-System\HaloCEMapDownloader\downloads')
    cService = webdriver.ChromeService(executable_path='D:\\Github\\Halo-CE-Map-Downloads-System\\HaloCEMapDownloader\\chromedriver.exe')
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
            file_path = os.path.join('D:\Github\Halo-CE-Map-Downloads-System\HaloCEMapDownloader\downloads', filename)
            with open(file_path, 'wb') as file:
                file.write(response.content)
            
            print(f"Downloaded file: {file_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    else:
        print("Target form not found.")

    browser.quit()

# Run the scraping function for the first URL
scrape_filelinks("https://www.halomaps.org/hce/index.cfm?sid=10")

# Run the scraping function for the second URL with Start parameter incremented by 30
for i in range(0, 400):  # Adjust the range based on how many times you want to increment Start
    start_value = 31 + i * 30
    url_page_one = f"https://www.halomaps.org/hce/index.cfm?sid=10&sort=1&Start={start_value}"
    scrape_filelinks(url_page_one)
