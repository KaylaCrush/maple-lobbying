from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import datetime, logging
from bs4 import BeautifulSoup as bs
from src.utils import pull_html

search_page_url = 'https://www.sec.state.ma.us/LobbyistPublicSearch/'

def get_lobbyist_urls(year):
    year = str(year)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    url = search_page_url

    logging.info(f"Pulling lobbyist urls for {year} from {url}")
    driver.get(url)

    ##setup the parameters and run the search
    lobbyist_radio_button = driver.find_element('id','ContentPlaceHolder1_rdbSearchByType')
    lobbyist_radio_button.click
    drop_down_boxes = driver.find_elements(By.CLASS_NAME,'p3')
    Select(drop_down_boxes[0]).select_by_value(year)
    Select(drop_down_boxes[-1]).select_by_index(0)
    Select(driver.find_element('id','ContentPlaceHolder1_ucSearchCriteriaByType_drpType')).select_by_value('L')
    driver.find_element('id','ContentPlaceHolder1_btnSearch').click()

    html = driver.page_source
    soup = bs(html, 'html.parser')

    url_list = []
    griditems = soup.find_all('a', class_=lambda tag: tag and tag=='BlueLinks', id=lambda tag: tag and 'SearchResultByTypeAndCategory' in tag)
    url_list = [url+item.attrs['href'] for item in griditems]
    driver.close()
    return url_list

def get_disclosure_urls(lobbyist_url):
    url = search_page_url
    logging.info(f"Pulling disclosure urls from {lobbyist_url}")
    html = pull_html(lobbyist_url)
    soup = bs(html, 'html.parser')
    results = soup.find_all('a', class_='BlueLinks', href=lambda tag: tag and 'CompleteDisclosure' in tag)
    url_list = [url+item.attrs['href'] for item in results]
    return url_list

def get_disclosures_by_year(year):
    lobbyist_urls = get_lobbyist_urls(year)
    disclosure_urls = []
    for url in lobbyist_urls:
        results = get_disclosure_urls(url)
        for result in results:
            disclosure_urls.append(result)
    return disclosure_urls

# def get_latest_disclosures():
#     year = datetime.date.today().year
#     lobbyist_urls = get_lobbyist_urls(year)
#     disclosure_urls = []
#     for url in lobbyist_urls:
#         results = get_disclosure_urls(url)
#         if results:
#             disclosure_urls.append(results[-1])
#     return disclosure_urls

def get_recent_disclosures():
    year = datetime.date.today().year
    return list(set(get_disclosures_by_year(year) + get_disclosures_by_year(year-1)))
