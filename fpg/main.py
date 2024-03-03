import fpg
import db


def fetch_data_from_list_url(url: str, * , stream_dst: str | None=None, list_idx: int=0) -> list:
    """
    list url (最大 20 件の一覧を表示するページ) を与えると、必要データを格納して返す関数。

    Parameters
    ----------
    url

    stream_dst : str
        戻り値以外に、別に sqlite3 に書き込むためのパス。(むしろ、戻り値は、単体テスト用に存在する)
        重複しないようにする等は、この関数の上位側の所掌とする。
    
    list_idx : int
    """
    result = []
    each_urls = fpg.list.fetch_all_each_page_urls(url)
    for each_idx, each_url in enumerate(each_urls):
        temp_result = {
            'list_idx': list_idx,  # INFO: 240302 並行処理で後から並び替え用にも使用
            'each_idx': each_idx,
        }
        temp = fpg.each.fetch_info_from_each_page(each_url)  # TODO: 240303 何の値を取得するかは、ここで指定できるようにせよ。config.json で設定がいいと思う。
        if temp is not None:
            temp_result.update(temp)
            result.append(temp_result)
            if stream_dst is not None:
                db.each.insert_one(args=temp_result, db_path=stream_dst)

    return result