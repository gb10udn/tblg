from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.sql import text
import datetime


class EachUrlTableHandler:
    def __init__(self, *, add_cols: list[str]=[], db_path: str='test.db'):  # HACK: 240303 .db ファイルが存在する場合の挙動を定義すること。
        """
        db ハンドラ

        Parameters
        ----------
        add_cols : list[str]
            動的に追加するカラム名。String で定義される。
            取得するカラム名を動的に変更できるため、動的な部分をこの引数で設定する。

        db_path : str
            sqlite 書き出す or 読み出すパス。
        """
        self._DATETIME_FORMAT = '%Y-%m-%d %H-%M-%S'
        self._FALSE = 0
        self._TRUE = 1

        self._db_path = db_path
        self._engine = create_engine('sqlite:///{}'.format(self._db_path), echo=False)
        Session = sessionmaker(bind=self._engine)
        self._session = Session()

        for col in add_cols:
            if not hasattr(EachUrlTable, col):
                setattr(EachUrlTable, col, Column(String))

        EachUrlTable.metadata.create_all(self._engine)
    

    def _obtain_now(self):
        return str(datetime.datetime.strftime(datetime.datetime.now(), self._DATETIME_FORMAT))
    

    def insert_one(self, args: dict[str, str]):
        """
        データを入力する関数。
        """
        mapper = EachUrlTable()
        mapper.created_at = datetime.datetime.strftime(datetime.datetime.now(), self._DATETIME_FORMAT)

        for key, val in args.items():
            setattr(mapper, key, val)

        self._session.add(mapper)
        self._session.commit()


    def close(self):
        self._session.rollback()
        self._session.close()
        self._engine.dispose()


class Base(DeclarativeBase):
    pass


class EachUrlTable(Base):
    """
    each_url (詳細のデータが格納されたページの URL) から取得したデータを格納するテーブル定義。
    取得するデータ (Ex. オープン日、ジャンル 等) は動的に変更できるため、その部分は後から追加するものとした。
    """
    __tablename__ = 'each_url'
    url = Column(String, primary_key=True)
    list_idx = Column(Integer)
    each_idx = Column(Integer)
    created_at = Column(String, nullable=False)


####
    

def insert_one(args: dict[str, str], db_path: str):
    """
    sqlite3 にデータを格納する関数。
    db_path が存在する場合、db_path に含まれないカラムが、args のキーに含まれる場合、エラーを返すので注意すること。  # HACK: 240303 正しくエラーを通知するようにする。
    """
    PRIMARY_KEY = 'url'
    assert PRIMARY_KEY in args.keys(), 'ArgError: args must contain PRIMARY_KEY -> "{}"'.format(PRIMARY_KEY)

    add_cols = list(args.keys())
    hdr = EachUrlTableHandler(add_cols=add_cols, db_path=db_path)
    try:
        hdr.insert_one(args=args)  # HACK: 240303 エラーハンドリングを記述せよ。
    finally:
        hdr.close()


def count(path: str) -> int:
    engine = create_engine('sqlite:///{}'.format(path), echo=False)  # FIXME: 240304 path が非存在のケースの記述が必要？
    Session = sessionmaker(bind=engine)
    session = Session()
    return len(list(session.execute(text("select * from each_url"))))