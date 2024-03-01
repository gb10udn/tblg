import requests
from bs4 import BeautifulSoup
from typing import Any
import re


class EachPage:
    def __init__(self, url: str):
        """
        個別ページでの処理と値を記述する。
        """
        self._url = url
        response = requests.get(self._url)
        assert response.ok, f'fail to access -> "{self._url}"'  # HACK: 240301 初期化失敗は、これを操作する関数が処理するものとする。
        self._soup = BeautifulSoup(response.text, 'html.parser')


    def _fetch_info_from_table(self, items: list[str] | str) -> dict[str, str | None]:
        """
        テーブル要素から、必要情報を取得する。
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
    

    def _fetch_rating_and_kuchikomi_num_and_bookmarked_num(self) -> dict[str, int | float | None]:
        """
        ヘッダ部から、評価点、口コミ数、ブックマーク登録数を取得する。
        """
        result: dict = {
            'rating': None,
            'kuchikomi_num': None,
            'bookmarked_num': None,
        }

        IDX = {
            'rating': 0,
            'kuchikomi_num': 1,
            'bookmarked_num': 2,
        }

        header = self._soup.find(id='js-header-rating')
        if header is None:
            return result
        
        li_list = header.find_all('li')
        if li_list is None:
            return result
        
        for idx, li in enumerate(li_list):
            text = li.text.strip()

            try:
                if idx == IDX['rating']:
                    rating_list = re.findall('[0-9]{1}.[0-9]{2}', text)
                    rating = float(rating_list[0])
                    result['rating'] = rating
                
                elif idx == IDX['kuchikomi_num']:
                    kuchikomi_num_list = re.findall('[0-9]{1}.[0-9]{2}|[0-9]{1,10}', text)
                    kuchikomi_num = int(kuchikomi_num_list[0])
                    result['kuchikomi_num'] = kuchikomi_num
                
                elif idx == IDX['bookmarked_num']:
                    bookmarked_num_list = re.findall('[0-9]{1}.[0-9]{2}|[0-9]{1,10}', text)
                    bookmarked_num = int(bookmarked_num_list[0])
                    result['bookmarked_num'] = bookmarked_num

            except:
                pass  # HACK: 240301 デバッグ時に気づきにくいので注意。
                
        return result