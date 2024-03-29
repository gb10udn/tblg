let button = document.createElement('button');
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
  }, 2000);


  fetch('http://localhost:5000/run').then(_ => {
    clearInterval(intervalId);
    setTimeout(() => {
      button.disabled = false;
      text.nodeValue = ' ダウンロード完了しました。'
    }, 3000)

  }).catch((err) => {
    button.disabled = false;
    clearInterval(intervalId);
    console.error('Error -> ', err);
    text.nodeValue = ' エラー発生しました。'
  });
};

// FIXME: 240305 画面閉じる際にバックエンドに通知して、バックエンドプロセスを終了させるといい