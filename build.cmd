CALL .\.pro\Scripts\activate
pyinstaller main.py --icon=icon.ico --add-data=.\ref\ui.js:.\ --add-data=.\ref\setting.json:.\ --onefile --noconsole
PAUSE