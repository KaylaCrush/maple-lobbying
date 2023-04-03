
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs

import datetime
from bs4 import BeautifulSoup as bs
from src.sql_manager import insert_table

search_page_url = 'https://www.sec.state.ma.us/LobbyistPublicSearch/'

def create_selenium_driver():
    options = ChromeOptions()
    options.add_argument('--incognito')
    options.add_argument('--start_maximized')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.wait = WebDriverWait(driver, 2)
    return driver

def create_uc_driver():
    options = uc.ChromeOptions()
    options.add_argument('--incognito')
    options.add_argument('--start_maximized')
    driver = uc.Chrome(options=options, use_subprocess=True)
    driver.wait = WebDriverWait(driver, 2)
    return driver

create_driver = create_selenium_driver

def pull_html(url, driver=None):
    this_driver = driver if driver else create_driver()
    this_driver.get(url)
    html = this_driver.page_source
    if driver == None: # If this function was not sent a driver, make sure you close the one we opened
        this_driver.close()
    return html

def get_disclosures_by_year(year, driver):
    lobbyist_urls = get_lobbyist_urls(year,driver)
    for lobbyist_url in lobbyist_urls:
        pull_disclosure_urls(lobbyist_url,driver)


def pull_disclosure_urls(lobbyist_url,driver):

    html = pull_html(lobbyist_url,driver)

    soup = bs(html, 'html.parser')

    entity = soup.find('span', id = 'ContentPlaceHolder1_lblRegistrantName').text
    year = soup.find('span', id = "ContentPlaceHolder1_lblYear").text
    results = soup.find_all('a', class_='BlueLinks', href=lambda tag: tag and 'CompleteDisclosure' in tag)
    disclosure_urls = [search_page_url+item.attrs['href'] for item in results]
    today = datetime.datetime.now().date()
    for url in disclosure_urls:
        row = (url, year, entity, today, None)
        insert_table('urls',columns=['url','year','entity','last_accessed','last_scraped'], rows = (row,))



##setup the parameters and run the search
def get_lobbyist_urls(year, driver):
    driver.get(search_page_url)
    # lobbyist_radio_button = driver.find_element('id','ContentPlaceHolder1_rdbSearchByType')
    # lobbyist_radio_button.click
    drop_down_boxes = driver.find_elements(By.CLASS_NAME,'p3')
    Select(drop_down_boxes[0]).select_by_value(year)
    Select(drop_down_boxes[-1]).select_by_index(0)
    Select(driver.find_element('id','ContentPlaceHolder1_ucSearchCriteriaByType_drpType')).select_by_value('L')
    driver.find_element('id','ContentPlaceHolder1_btnSearch').click()
    html = driver.page_source

    soup = bs(html, 'html.parser')
    griditems = soup.find_all('a', class_=lambda tag: tag and tag=='BlueLinks', id=lambda tag: tag and 'SearchResultByTypeAndCategory' in tag)
    url_list = [search_page_url+item.attrs['href'] for item in griditems]
    return url_list



