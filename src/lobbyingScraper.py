import datetime, logging, requests
from bs4 import BeautifulSoup as bs
from src.utils import pull_html

search_page_url = 'https://www.sec.state.ma.us/LobbyistPublicSearch/'

def get_lobbyist_urls(year):
    year = str(year)

    # modified from https://stackoverflow.com/questions/69616689/parsing-aspx-site-with-python-post-request
    url = search_page_url
    with requests.Session() as s:
        s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        r = s.get("https://www.sec.state.ma.us/LobbyistPublicSearch/")
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
