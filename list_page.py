import requests
from bs4 import BeautifulSoup


def fetch_each_page_url_list(url: str) -> list[str]:
    """
    一覧ページから、個別 URL のリストを取得する関数
    """
    response = requests.get(url)
    if response.ok == False:
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    a_list = soup.find_all(name='a', class_='list-rst__rst-name-target')
    if a_list is None:
        return []
    else:
        return [a['href'] for a in a_list]