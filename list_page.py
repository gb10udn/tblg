import requests
from bs4 import BeautifulSoup
import re


class ListPage:
    def __init__(self, url: str):
        """
        一覧ページから、必要な URL を全件取得する。(その後、each_page.py が処理する想定)
        ページ遷移は、この関数の所掌範囲外とする。
        """
        self._url = url
        response = requests.get(self._url)
        assert response.ok, f'fail to access -> "{self._url}"'  # HACK: 240301 初期化失敗は、これを操作する関数が処理するものとする。
        self._soup = BeautifulSoup(response.text, 'html.parser')


    def fetch_each_page_url_list(self) -> list[str]:
        a_list = self._soup.find_all(name='a', class_='list-rst__rst-name-target')
        if a_list is None:
            return []
        else:
            return [a['href'] for a in a_list]