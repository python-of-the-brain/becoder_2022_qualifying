from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--headless")

CHROME_DRIVER_PATH = "./chromedriver"

service = Service(executable_path=CHROME_DRIVER_PATH)

driver = webdriver.Chrome(
    service=service,
    chrome_options=chrome_options,
)

driver.get('https://mail.ru')