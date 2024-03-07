from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from selenium import webdriver
import uvicorn
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import datetime
import os
import sys
import signal

import fpg
import db


sys.stdout = open(os.devnull, 'w')  # INFO: 240305 --nocosole で必要。(FastAPI がエラーで落ちる。)

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
    return 'welcome to tblg app !!!'

@app.get('/run')
def run():
    """
    食べログで必要データを取得する処理を開始する。
    """
    # [START] set up parames
    MAX_THREAD_NUM = 5
    RESTRICT_URL_NUM = 5  # INFO: 240307 お試し版では、2 や、3 にしておく。None にすると、制約かからない。
    # [END] set up parames

    global sql_dst
    print('処理開始')
    t0 = time.time()
    
    url = driver.current_url
    pass  # TODO: 240303 検索条件を保存できるようにする。 (url から取得する関数を作る。)
    all_list_urls = fpg.list.fetch_all_list_page_urls(url)

    now = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
    sql_dst = f'logs/{now}.db'
    sql_dst_dir = os.path.dirname(sql_dst)
    os.makedirs(sql_dst_dir, exist_ok=True)

    pool = ThreadPoolExecutor(max_workers=MAX_THREAD_NUM)
    for list_idx, list_url in enumerate(all_list_urls[:RESTRICT_URL_NUM]):  # TODO: 240307 この部分に制約を付けて、無料お試し版として販売する？
        kwargs = {
            'url': list_url,
            'stream_dst': sql_dst,
            'list_idx': list_idx,
        }
        pool.submit(fpg.fetch_data_from_list_url, **kwargs)
    pool.shutdown()

    run_time = time.time() - t0  # TODO: 240303 logs ディレクトリの sqlite3 の別のテーブルにデータを格納する。
    db.common.export(src=sql_dst, dst=f'{now}.csv')


@app.get('/status')
def status():
    """
    ダウンロード中の進捗状況を取得する。
    """
    count = db.each.count(sql_dst)
    total = fpg.list.fetch_total_url_num(driver.current_url)
    return ' ダウンロード中: {} / {}'.format(count, total)


@app.get('/killme')
def killme():
    """
    Python に起因するプロセスを終了するための関数。
    """
    try:
        driver.quit()
    except:
        pass
    try:
        event.clear()
    except:
        pass
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)


@app.get('/pid')
def pid():
    """
    プロセス id 取得。強制終了する用途。
    """
    return os.getpid()


def create_button_daemon(*, sleep_time=0.5) -> None:
    """
    url が更新されていれば、バックエンドと通信するボタンを設置する関数。
    threading で並行処理として呼ばれる想定。
    """
    js_ui_script_path = obtain_ref_path(file_name='ui.js')
    with open(js_ui_script_path, 'r', encoding='utf-8') as f:
        js_script = f.read()

    url = ''
    while True:
        if (driver.current_url != url) and ('https://tabelog.com/' in driver.current_url) and ('rstLst/?' in driver.current_url):
            driver.execute_script(js_script)
        try:
            url = driver.current_url
        except:
            break  # INFO: 240305 webdriver が閉じられると、こっちに流れてくる (driver.current_url が取得できないため)
        time.sleep(sleep_time)


def obtain_ref_path(file_name: str, *, base_dir: str='./ref') -> str:
    """
    ファイル名を指定すると、実行環境 (.exe or .py) に応じて適切なファイルパスを返す関数。
    """
    call_from_pyinstaller = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')  # INFO: 240305 https://www.pyinstaller.org/en/stable/runtime-information.html?highlight=sys._MEIPASS#run-time-information
    if call_from_pyinstaller == True:
        result = '{}/{}'.format(sys._MEIPASS, file_name)  # type: ignore  # INFO: 2403006 to ignore mypy check
    else:
        result = '{}/{}'.format(base_dir, file_name)
    return result


if __name__ == '__main__':
    global driver
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ['enable-automation'])  # INFO: 240306 「Chromeは自動テストソフトウェアによって制御されています」を非表示にする。
    driver = webdriver.Chrome(options=options)
    driver.get('https://tabelog.com/')
    
    global event
    event = threading.Event()
    sub_thread = threading.Thread(target=create_button_daemon, daemon=True)
    sub_thread.start()
    event.set()

    try:
        requests.get('http://localhost:5000/killme')  # INFO: 240305 前のプロセスが残っている場合は削除する。
    finally:
        uvicorn.run(app, host="127.0.0.1", port=5000)  # TODO: 240302 空いたポート番号を発見して割り当てるようにせよ。