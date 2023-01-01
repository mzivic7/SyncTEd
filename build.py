import os
import shutil
from sys import platform

if platform == "win32":
    os.system('pyinstaller --noconfirm --onedir --windowed --clean --add-data "data:data/" --name "SyncTEd" "main.py"')
else:
    os.system('python -m PyInstaller --noconfirm --onedir --windowed --clean --add-data "data:data/" --name "SyncTEd" "main.py"')

os.remove('SyncTEd.spec')
shutil.rmtree('build')
shutil.rmtree('__pycache__')
shutil.copytree('dist/', './', dirs_exist_ok=True)
shutil.rmtree('dist')
