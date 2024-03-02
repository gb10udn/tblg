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
    return {'Hello': 'World'}

@app.get('/run')
def run():
    """
    食べログで必要データを取得する処理を開始する。
    """
    print('処理開始')
    
    url = driver.current_url
    all_list_urls = fpg.list.fetch_all_list_page_urls(url)

    result = []
    for list_url in all_list_urls:  # HACK: 240302 少し遅いので、並行処理でやるといいかも？また、フロントエンドに処理状況を渡すといいかも？
        each_urls = fpg.list.fetch_all_each_page_urls(list_url)
        for each_url in each_urls:
            temp_result = fpg.each.fetch_info_from_each_page(each_url)
            if temp_result is not None:
                result.append(temp_result)
    
    result = pd.DataFrame(result)
    result.to_csv('test_.csv', encoding='shift-jis')  # TODO: 240302 ファイル名に検索や、プログラムバージョンを含めるといいかも？


####


global driver


def create_button_daemon(*, sleep_time=0.5):
    """
    url が更新されていれば、バックエンドと通信するボタンを設置する関数。
    threading で並行処理として呼ばれる想定。
    """

    JS_SCRIPT = '''let button = document.createElement("button");
button.innerHTML = "Click me";
button.onclick = () => {
fetch("http://localhost:5000/run");
};
document.body.insertBefore(button, document.body.firstChild);'''

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
    except:
        event.clear()