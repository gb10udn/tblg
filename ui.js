let button = document.createElement('button');  // HACK: 240305 const で行けそう
button.innerHTML = 'ダウンロード';
document.body.insertBefore(button, document.body.firstChild);

let text = document.createTextNode('');  // HACK: 240305 const で行けそう
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
    text.nodeValue = ' ダウンロード完了しました。'  // FIXME: 240306 即実行すると、ダウンロード完了しましたの処理の後に、fetch の戻りが来て、更新される場合があるっぽいので修正せよ。

  }).catch((err) => {
    button.disabled = false;
    clearInterval(intervalId);
    console.error('Error -> ', err);
    text.nodeValue = ' エラー発生しました。'
  });
};

// FIXME: 240305 画面閉じる際にバックエンドに通知して、バックエンドプロセスを終了させるといい