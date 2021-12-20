import os
import shutil

os.system('pyinstaller --noconfirm --onedir --windowed --clean --name "SyncTEd" --add-data "data:data/"  "main.py"')

os.remove('SyncTEd.spec')
shutil.rmtree('build')
shutil.rmtree('__pycache__')
shutil.copytree('dist/', './', dirs_exist_ok=True)
shutil.rmtree('dist')
