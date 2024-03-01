import sys
sys.path.append('./')

import fpg


def test_fetch_info_from_table():
    url = 'https://tabelog.com/osaka/A2706/A270604/27020108/'
    ep = fpg.each.EachPage(url)
    result = ep.fetch_info_from_table(['店名'])
    assert result == {'店名': '木曽路 高槻店（キソジ）'}


def test_fetch_rating_and_kuchikomi_num_and_bookmarked_num():
    url = 'https://tabelog.com/osaka/A2706/A270604/27020108/'
    ep = fpg.each.EachPage(url)
    result = ep.fetch_rating_and_kuchikomi_num_and_bookmarked_num()
    expected = {
        'rating': 3.07,  # INFO: 240301 実行時にその時の値を更新しないとダメ。
        'kuchikomi_num': 23,
        'bookmarked_num': 376,
    }
    assert result == expected