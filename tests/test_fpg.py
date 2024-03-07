import sys
sys.path.append('./')

import fpg


def test_fetch_info_from_table():
    url = 'https://tabelog.com/osaka/A2706/A270604/27020108/'  # HACK: 240303 bs4 の単体テストという意味では、html ファイルからパースするルートがあってもいいと思う。
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


def test_fetch_all_list_page_urls():
    """
    fpg.list.fetch_all_list_page_urls の単体テスト。
    ページ数が少ない場合のテストがメイン。(エラー出したことがあったので。)
    """
    # INFO: 240302 ↓ 結果は 18 件 (< 20) で、１ページのみですべてが表示できるタイプ
    url = 'https://tabelog.com/rstLst/?utf8=%E2%9C%93&vs=1&sa=%E9%AB%98%E6%A7%BB%E5%B8%82&hfc=0&pal=osaka&LstPrf=C27207&SrtT=trend&lid=&RdoCosTp=2&LstCos=8&LstCosT=0&search_date=2024%2F3%2F3%28%E6%97%A5%29&svd=20240303&svps=2&svt=1900&LstRev=0&commit=%E7%B5%9E%E3%82%8A%E8%BE%BC%E3%82%80&LstSitu=0&LstSmoking=0'
    result = fpg.list.fetch_all_list_page_urls(url)
    assert len(result) == 1

    # INFO: 240302 ↓ 結果は 34 件で、２ページで結果が表示できるもの。
    url = 'https://tabelog.com/rstLst/?utf8=%E2%9C%93&utf8=%E2%9C%93&vs=1&sa=%E9%AB%98%E6%A7%BB%E5%B8%82&hfc=0&pal=osaka&LstPrf=C27207&SrtT=trend&commit=%E7%B5%9E%E3%82%8A%E8%BE%BC%E3%82%80&trailing_slash=true&lid=&RdoCosTp=2&LstCos=6&LstCosT=0&search_date=2024%2F3%2F4%28%E6%9C%88%29&svd=20240304&svps=2&svt=1900&LstRev=0&commit=%E7%B5%9E%E3%82%8A%E8%BE%BC%E3%82%80&LstSitu=0&LstSmoking=0'
    result = fpg.list.fetch_all_list_page_urls(url)
    assert len(result) == 2