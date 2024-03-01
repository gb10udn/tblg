from typing import List
import requests
from bs4 import BeautifulSoup


class EachPage:
    def __init__(self, url: str):
        """
        各ページでの処理と値を記述する。
        """
        self._url = url
        response = requests.get(self._url)
        assert response.ok, f'fail to access -> "{self._url}"'  # HACK: 240301 初期化失敗は、これを操作する関数が処理するものとする。
        self._soup = BeautifulSoup(response.text, 'html.parser')


    def _fetch_info_from_table(self, items: List[str]|str) -> dict[str, str | None]:
        """
        個別ページのテーブル要素から、必要情報を取得する。
        必要情報は、item で定義し、table 要素の tr と一致した場合にその値を返す。
        """
        if type(items) == str:
            items = [items]
        result: dict = {item: None for item in items}    
        
        table_list = self._soup.find_all(name='table')
        for table in table_list:
            for tr in table.find_all('tr'):  # INFO: 240301 tr の中には、th, td が１つずつのみある想定
                th = tr.find('th')
                td = tr.find('td')
                if (th is not None) and (td is not None) and th.text in items:
                    result[th.text] = td.text.strip()

        return result