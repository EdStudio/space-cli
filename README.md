# Space CLI

## Installation

```bash
git clone https://github.com/EnzoDeg40/space-cli.git
cd space-cli
pip install -r requirements.txt
python main.py --username enzo --password enzo
```

## Build executable

```bash
pip install pyinstaller
pyinstaller --onefile main.py --name space --icon=assets/icon.ico
```