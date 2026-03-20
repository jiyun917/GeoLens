@echo off
set PATH=C:\Program Files (x86)\Microsoft Visual Studio\Installer;%PATH%
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" amd64
set PATH=C:\Users\user\AppData\Local\Programs\Python\Python312;C:\Users\user\AppData\Local\Programs\Python\Python312\Scripts;%PATH%
cd /d C:\Users\user\Downloads\GeoLens-develop\GeoLens-develop
.venv\Scripts\python.exe -m pip install -r requirements.txt
