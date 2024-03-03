from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from selenium import webdriver
import uvicorn
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import datetime
import pandas as pd  # HACK: 240302 pyinstaller 的に重くなるので、sqlalchemy でやるなどしたらいいかも？

import fpg


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # INFO: 240302 for CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

@app.get('/')
def read_root():
    return 'tblg'

@app.get('/run')
def run():
    """
    食べログで必要データを取得する処理を開始する。

    240303
    ------
    - TODO: 並行処理                     : 現状、1sec/件 でさすがに遅い気がする 
    - TODO: 処理状況をフロントに通知する : ボタンを何度もクリックできるのが問題。せめて、「処理中」くらいは表現する
    - TODO: ボタンの表現をリッチする     : できれば、フロートで常に表示されているようにしたい。
    - TODO: アイコン                     : 渡すときの感動はここにあると思う
    - TODO: ビルド                       : pyinstaller でビルドして動くかどうか。pandas が邪魔になりそう。
    """
    print('処理開始')
    t0 = time.time()
    
    url = driver.current_url
    pass  # TODO: 240303 検索条件を保存できるようにする。
    all_list_urls = fpg.list.fetch_all_list_page_urls(url)

    MAX_THREAD_NUM = 5  # HACK: 240303 最適な数値を選択する or フロントから変更できるようにする。
    now = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
    dst = f'{now}.db'

    pool = ThreadPoolExecutor(max_workers=MAX_THREAD_NUM)
    for list_idx, list_url in enumerate(all_list_urls):
        kwargs = {
            'url': list_url,
            'stream_dst': dst,
            'list_idx': list_idx,
        }
        pool.submit(fpg.fetch_data_from_list_url, **kwargs)
    pool.shutdown()
    print(time.time() - t0)  # TODO: 240303 log 的なところに吐き出せるようにせよ。また、timer クラスを作ってもいいかも？

    pass  # TODO: 240303 pandas 使わずに、csv に、shift-jis で出力する。


####


global driver


def create_button_daemon(*, sleep_time=0.5):
    """
    url が更新されていれば、バックエンドと通信するボタンを設置する関数。
    threading で並行処理として呼ばれる想定。
    """

    # TODO: 240302 この部分をもう少しリッチにすると、使いやすくなる気がする。
    JS_SCRIPT = '''
        let button = document.createElement("button");
        button.innerHTML = "ダウンロード";
        button.onclick = () => {
            fetch("http://localhost:5000/run");
        };
        document.body.insertBefore(button, document.body.firstChild);
    '''

    url = ''
    while True:
        if (driver.current_url != url) and ('https://tabelog.com/' in driver.current_url) and ('rstLst/?' in driver.current_url):
            driver.execute_script(JS_SCRIPT)
        url = driver.current_url
        time.sleep(sleep_time)


if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.get('https://tabelog.com/')
    
    event = threading.Event()
    sub_thread = threading.Thread(target=create_button_daemon, daemon=True)
    sub_thread.start()
    event.set()

    try:
        uvicorn.run(app, host="127.0.0.1", port=5000)  # TODO: 240302 空いたポート番号を発見して割り当てるようにせよ。
    finally:
        event.clear()