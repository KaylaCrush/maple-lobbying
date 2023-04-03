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


def get_disclosures_by_year(year, driver):
    lobbyist_urls = get_lobbyist_urls(year,driver)
    for lobbyist_url in lobbyist_urls:
        pull_disclosure_urls(lobbyist_url)
