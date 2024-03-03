from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from selenium import webdriver
import uvicorn
import threading
import time
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
    all_list_urls = fpg.list.fetch_all_list_page_urls(url)

    result = []
    for list_idx, list_url in enumerate(all_list_urls):  # TODO: 240302 並行処理で実施する https://tokitsubaki.com/python-asynchronous/460/
        fpg.fetch_data_from_list_url(list_url=list_url, list_idx=list_idx)
    
    result = pd.DataFrame(result)
    result.to_csv('test_.csv', encoding='shift-jis')  # TODO: 240302 ファイル名に検索や、プログラムバージョンを含めるといいかも？
    print(time.time() - t0)  # TODO: 240303 log 的なところに吐き出せるようにせよ。


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