import sys
sys.path.append('./')

import each_page


def test__fetch_info_from_table():
    url = 'https://tabelog.com/osaka/A2706/A270604/27020108/'
    ep = each_page.EachPage(url)
    result = ep._fetch_info_from_table(['店名'])
    assert result == {'店名': '木曽路 高槻店（キソジ）'}