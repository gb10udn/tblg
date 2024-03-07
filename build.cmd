CALL .\.pro\Scripts\activate
pyinstaller main.py --icon=icon.ico --add-data=.\ref\ui.js:.\ --onefile --noconsole
PAUSE