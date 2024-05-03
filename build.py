import os
import shutil
import sys

if sys.platform == "win32":
    os.system('python -m PyInstaller --noconfirm --onedir --windowed --clean --contents-directory "libraries" --name "SyncTEd" "main.py"')
elif sys.platform == "linux":
    os.system('python -m PyInstaller --noconfirm --onedir --windowed --clean --contents-directory "libraries" --name "SyncTEd" "main.py"')
else:
    print("This platform is not supported: " + sys.platform)
    sys.exit()

shutil.copytree("data/", "dist/SyncTEd/data/", dirs_exist_ok=True)
shutil.copy("LiberationMono-Regular.ttf", "dist/SyncTEd/LiberationMono-Regular.ttf")
