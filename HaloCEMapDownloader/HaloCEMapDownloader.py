from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

URL = "http://hce.halomaps.org/index.cfm?PG=1"

cService = webdriver.ChromeService(executable_path='D:\\Github\\Halo-CE-Map-Downloads-System\\HaloCEMapDownloader\\chromedriver.exe')
browser = webdriver.Chrome(service = cService)

browser.get(URL)
browser.implicitly_wait(320)
html = browser.page_source
soup = BeautifulSoup(html, "html.parser")
a = soup.find(class_='tbl')
print(soup)

browser.quit()  # Make sure to close the browser after using it

