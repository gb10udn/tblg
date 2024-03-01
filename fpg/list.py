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
    

    def fetch_total_url_num(self) -> int | None:
        """
        全何件が検索結果として表示されているかを確認する。
        """
        div_list = self._soup.find_all('div', class_='c-page-count')
        if div_list is None or len(div_list) > 1:
            return None
        
        div = div_list[0]  # INFO: 240302 ここの要素は１つだけの想定
        span_list = div.find_all('span', class_='c-page-count__num')
        if span_list is None:
            return None
        
        try:
            return int(span_list[-1].text.strip())
        except:
            return None