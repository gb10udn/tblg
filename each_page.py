from typing import List, Any, Optional
import requests
from bs4 import BeautifulSoup


def fetch_info_from_table(url: str, items: List[str]) -> dict[str, str | None]:
    """
    個別ページのテーブル要素から、必要情報を取得する。
    必要情報は、item で定義し、table 要素の tr と一致した場合にその値を返す。
    """
    result: dict = {item: None for item in items}    
    response = requests.get(url)
    if response.ok == False:
        return result  # HACK: 240301 エラーのことを伝えてもいいと思う。
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table_list = soup.find_all(name='table')
    for table in table_list:
        for tr in table.find_all('tr'):  # INFO: 240301 tr の中には、th, td が１つずつのみある想定
            th = tr.find('th')
            td = tr.find('td')
            if (th is not None) and (td is not None) and th.text in items:
                result[th.text] = td.text

    return result