from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from selenium import webdriver
import uvicorn
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import datetime
import os

import fpg
import db


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
    """
    global sql_dst

    print('処理開始')
    t0 = time.time()
    
    url = driver.current_url
    pass  # TODO: 240303 検索条件を保存できるようにする。 (url から取得する関数を作る。)
    all_list_urls = fpg.list.fetch_all_list_page_urls(url)

    MAX_THREAD_NUM = 5
    now = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S')
    sql_dst = f'logs/{now}.db'
    sql_dst_dir = os.path.dirname(sql_dst)
    os.makedirs(sql_dst_dir, exist_ok=True)

    pool = ThreadPoolExecutor(max_workers=MAX_THREAD_NUM)
    for list_idx, list_url in enumerate(all_list_urls):
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


####


def create_button_daemon(*, sleep_time=0.5, read_js_file=False):  # HACK: 240305 ビルド時に手動で組み込むのは少し手間かな。
    """
    url が更新されていれば、バックエンドと通信するボタンを設置する関数。
    threading で並行処理として呼ばれる想定。
    """

    if read_js_file == True:
        JS_BUTTON_SCRIPT_PATH = './ui.js'
        with open(JS_BUTTON_SCRIPT_PATH, 'r', encoding='utf-8') as f:
            js_script = f.read()

    else:
        js_script = '''let button = document.createElement('button');
button.innerHTML = 'ダウンロード';
document.body.insertBefore(button, document.body.firstChild);

let text = document.createTextNode('');
document.body.insertBefore(text, button.nextSibling);
document.body.insertBefore(button, text);

button.onclick = () => {
  button.disabled = true

  const intervalId = setInterval(() => {
    fetch("http://localhost:5000/status")
      .then(response => response.text())
      .then(data => {
        if (data.startsWith('"')) {
          data = data.slice(1)
        }
        if (data.endsWith('"')) {
          data = data.slice(0, -1)
        }
        text.nodeValue = data
      })
      .catch(err => {
        console.error('Error -> ', err);
      });    
  }, 1000);


  fetch('http://localhost:5000/run').then(_ => {
    button.disabled = false;
    clearInterval(intervalId);
    text.nodeValue = ' ダウンロード完了しました。'

  }).catch((err) => {
    button.disabled = false;
    clearInterval(intervalId);
    console.error('Error -> ', err);
    text.nodeValue = ' エラー発生しました。'
  });
};'''

    url = ''
    while True:
        if (driver.current_url != url) and ('https://tabelog.com/' in driver.current_url) and ('rstLst/?' in driver.current_url):
            driver.execute_script(js_script)

        url = driver.current_url
        time.sleep(sleep_time)


if __name__ == '__main__':
    global driver
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