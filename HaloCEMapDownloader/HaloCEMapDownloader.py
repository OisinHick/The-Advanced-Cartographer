""" 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "http://hce.halomaps.org/index.cfm?PG=1"

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

# Find an element with the class 'filelink'
filelink_element = soup.find('a', class_='filelink')

# Print the content of the found element
print(filelink_element)

browser.quit()



 """

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "http://hce.halomaps.org/index.cfm?PG=1"

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
