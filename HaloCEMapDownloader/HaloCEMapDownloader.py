""" 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "http://hce.halomaps.org/index.cfm?PG=1"
URLPageOne = "http://hce.halomaps.org/index.cfm?PG=1&sid=0&Start=21&sort=1&cd=0&fc=0&fc2=0"

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode

# Provide the path to the ChromeDriver executable
cService = webdriver.ChromeService(executable_path='D:\\Github\\Halo-CE-Map-Downloads-System\\HaloCEMapDownloader\\chromedriver.exe')
browser = webdriver.Chrome(service=cService, options=chrome_options)

browser.get(URL)
browser.implicitly_wait(320)
html = browser.page_source
soup = BeautifulSoup(html, "html.parser")

# Find all elements with the class 'filelink'
filelink_elements = soup.find_all('a', class_='filelink')

# Print the content of each found element
for filelink_element in filelink_elements:
    print(filelink_element)

browser.quit()
 """

# http://hce.halomaps.org/index.cfm?PG=1&sid=0&Start=61&sort=1&cd=0&fc=0&fc2=0
# http://hce.halomaps.org/index.cfm?PG=1&sid=0&Start=81&sort=1&cd=0&fc=0&fc2=0

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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

    # Print the content of each found element
    for filelink_element in filelink_elements:
        print(filelink_element)

    browser.quit()

# Run the scraping function for the first URL
scrape_filelinks("http://hce.halomaps.org/index.cfm?PG=1")

# Run the scraping function for the second URL with Start parameter incremented by 20
for i in range(0, 10):  # Adjust the range based on how many times you want to increment Start
    start_value = 21 + i * 20
    url_page_one = f"http://hce.halomaps.org/index.cfm?PG=1&sid=0&Start={start_value}&sort=1&cd=0&fc=0&fc2=0"
    scrape_filelinks(url_page_one)
