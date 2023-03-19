import datetime, logging, requests
from bs4 import BeautifulSoup as bs
from src.utils import insert_table

search_page_url = 'https://www.sec.state.ma.us/LobbyistPublicSearch/'

def get_lobbyist_urls(year):
    year = str(year)

    # modified from https://stackoverflow.com/questions/69616689/parsing-aspx-site-with-python-post-request
    url = search_page_url
    with requests.Session() as s:
        s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        r = s.get(search_page_url)
        soup = bs(r.text,"lxml")
        data = {i['name']:i.get('value','') for i in soup.select('input[name]')}

        data['ctl00$ContentPlaceHolder1$Search'] = "rdbSearchByType",
        data["ctl00$ContentPlaceHolder1$ucSearchCriteriaByType$ddlYear"] = year,
        data["ctl00$ContentPlaceHolder1$ucSearchCriteriaByType$txtN_ame"] = "",
        data["ctl00$ContentPlaceHolder1$ucSearchCriteriaByType$txtName_Watermark_ClientState"] = "",
        data["ctl00$ContentPlaceHolder1$ucSearchCriteriaByType$lddSearchType$DropDown"] = "3",
        data["ctl00$ContentPlaceHolder1$ucSearchCriteriaByType$drpType"] = "L",
        data["ctl00$ContentPlaceHolder1$drpPageSize"] = "20000",
        data["ctl00$ContentPlaceHolder1$btnSearch"] = "Search"

        p = s.post('https://www.sec.state.ma.us/LobbyistPublicSearch/Default.aspx', data=data)

        html = p.content

    soup = bs(html, 'html.parser')
    griditems = soup.find_all('a', class_=lambda tag: tag and tag=='BlueLinks', id=lambda tag: tag and 'SearchResultByTypeAndCategory' in tag)
    url_list = [url+item.attrs['href'] for item in griditems]
    return url_list


def get_disclosures_by_year(year):
    lobbyist_urls = get_lobbyist_urls(year)
    for lobbyist_url in lobbyist_urls:
        pull_disclosure_urls(lobbyist_url)


def pull_disclosure_urls(lobbyist_url):
    base_url = "https://www.sec.state.ma.us/LobbyistPublicSearch/"

    html = pull_html(lobbyist_url)

    soup = bs(html, 'html.parser')

    entity = soup.find('span', id = 'ContentPlaceHolder1_lblRegistrantName').text
    year = soup.find('span', id = "ContentPlaceHolder1_lblYear").text
    results = soup.find_all('a', class_='BlueLinks', href=lambda tag: tag and 'CompleteDisclosure' in tag)
    disclosure_urls = [base_url+item.attrs['href'] for item in results]
    today = datetime.datetime.now().date()
    for url in disclosure_urls:
        row = (url, year, entity, today, None)
        insert_table('urls',columns=['url','year','entity','last_accessed','last_scraped'], rows = (row,))



####
# SELENIUM METHODS
####

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup as bs
search_page_url = 'https://www.sec.state.ma.us/LobbyistPublicSearch/'

def create_headless_selenium():
    #options = ChromeOptions()
    options = uc.ChromeOptions()
    options.add_argument('--incognito')
    #options.add_argument('--headless')
    options.add_argument('--start_maximized')
    #service = Service(ChromeDriverManager().install())
    driver = uc.Chrome(options=options, use_subprocess=True)
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.wait = WebDriverWait(driver, 2)
    return driver


def pull_html(url):
    driver = create_headless_selenium()
    driver.get(url)
    html = driver.page_source
    driver.close()
    return html

##setup the parameters and run the search
def gather_lobbyist_urls(year):
    with create_headless_selenium() as driver:
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
