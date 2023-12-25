
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin

DownloadUrl = "http://hce.halomaps.org/index.cfm?fid=7129"

# Scrapes the URLs for the page and formatting to be just the links
def scrape_filelinks(url):
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode

    # Provide the path to the ChromeDriver executable
    cService = webdriver.ChromeService(executable_path='D:\\Github\\Halo-CE-Map-Downloads-System\\HaloCEMapDownloader\\chromedriver.exe')
    browser = webdriver.Chrome(service=cService, options=chrome_options)

    browser.get(url)
    browser.implicitly_wait(320)
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Find all elements with the class 'filelink'
    filelink_elements = soup.find_all('a', class_='filelink')

    # Extract href attribute and create complete URL
    for filelink_element in filelink_elements:
        href_value = filelink_element.get('href')
        if href_value:
            complete_url = urljoin("http://hce.halomaps.org/", href_value)
            print(complete_url)
            scrape_filelinks_download(complete_url)

    browser.quit()

# Scrapes the URLs for the page and formatting to be just the links
def scrape_filelinks_download(url):

    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode
    chrome_options.add_argument(f'--download.default_directory=D:\Github\Halo-CE-Map-Downloads-System\HaloCEMapDownloader\downloads')

    # Provide the path to the ChromeDriver executable
    cService = webdriver.ChromeService(executable_path='D:\\Github\\Halo-CE-Map-Downloads-System\\HaloCEMapDownloader\\chromedriver.exe')
    browser = webdriver.Chrome(service=cService, options=chrome_options)

    browser.get(url)
    browser.implicitly_wait(320)
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    print(soup)

    browser.quit()

# Run the scraping function for the first URL
scrape_filelinks("http://hce.halomaps.org/index.cfm?PG=1")

# Run the scraping function for the second URL with Start parameter incremented by 20
for i in range(0, 400):  # Adjust the range based on how many times you want to increment Start
    start_value = 21 + i * 20
    url_page_one = f"http://hce.halomaps.org/index.cfm?PG=1&sid=0&Start={start_value}&sort=1&cd=0&fc=0&fc2=0"
    scrape_filelinks(url_page_one)
