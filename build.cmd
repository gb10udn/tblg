CALL .\.pro\Scripts\activate
pyinstaller main.py --icon=icon.ico --add-data=.\ui.js:.\ --onefile --noconsole
PAUSE