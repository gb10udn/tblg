from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from selenium import webdriver
import uvicorn
import threading
import time


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # INFO: 220818 CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

@app.get('/')
def read_root():
    return {'Hello': 'World'}

@app.get('/run')
def run():
    print('ここはきたよおおおおおおおおお')
    pass  # EDIT: 240302 ダウンロード処理を開始する。


####


global driver

port_num = 5000




def update_button(*, sleep_time=0.5):
    """
    url が更新されていれば、バックエンドと通信するボタンを設置する関数。
    threading で並行処理として呼ばれる想定
    """

    JS_SCRIPT = '''let button = document.createElement("button");
button.innerHTML = "Click me";
button.onclick = () => {
fetch("http://localhost:5000/run");
};
document.body.insertBefore(button, document.body.firstChild);'''

    url = ''
    while True:
        if driver.current_url != url:
            driver.execute_script(JS_SCRIPT)
        url = driver.current_url
        time.sleep(sleep_time)


if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.get('https://tabelog.com/')
    
    event = threading.Event()
    sub_thread = threading.Thread(target=update_button, daemon=True)
    sub_thread.start()
    event.set()

    uvicorn.run(app, host="127.0.0.1", port=5000)

    event.clear()