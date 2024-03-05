from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import os
import csv
from db.each import EachUrlTable

# TODO: 240303 log から、検索結果を表示して、取得した結果を再度ダウンロードできるビューアーを実装すると再利用性が高まっていいかも？


def export(src: str, dst: str, *, encoding: str='shift-jis') -> None:  # HACK: 240303 単体テスト可能な形で実装せよ。 (改行 / None の件はテストコードが必要と思う。)
    """
    sqlite のファイルパス (src) を与えると、中身のデータを出力する関数。
    """
    # [START] obtain keys
    engine = create_engine('sqlite:///{}'.format(src), echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    keys = list(session.execute(text("select * from each_url")).keys())
    # [END] obtain keys

    try:
        # [START] set up mapper
        for key in keys:
            if not hasattr(EachUrlTable, key):
                setattr(EachUrlTable, key, Column(String))  # INFO: 240304 クラスで定義されていないものはすべて String であるものとする。
        # [END] set up mapper

        dir_path = os.path.dirname(src)
        os.makedirs(dir_path,exist_ok=True)
        with open(dst, 'w', newline='', encoding=encoding) as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)  # INFO: 240305 \n 対策で、ダブルクオーテーションで囲う
            writer.writerow(keys)
            iter = session.query(EachUrlTable).order_by(EachUrlTable.list_idx, EachUrlTable.each_idx)
            for i in iter:
                oneline = [str(getattr(i, key)) if getattr(i, key) is not None else '' for key in keys]
                if encoding == 'shift-jis':  # HACK: 240304 enum で encoding を指定する。
                    oneline = [_replace_shift_jis_unsupported_characters(i) for i in oneline]  # INFO: 240304 店名は特殊文字で shift-jis に変換できないものがあった。
                writer.writerow(oneline)
    
    finally:
        # [START] close sqlite
        session.rollback()
        session.close()
        engine.dispose()
        # [END] close sqlite


def _replace_shift_jis_unsupported_characters(arg: str, *, replacement_char='@') -> str:
    """
    shift-jis でエンコードできない文字列を置き換える関数。
    """
    result = ""
    for char in arg:
        try:
            char.encode('shift-jis')
            result += char
        except UnicodeEncodeError:
            result += replacement_char

    return result