@echo off
chcp 65001 > nul
set PYTHONUTF8=1

REM Find streamlit executable
set STREAMLIT_EXE=C:\Users\hdy73\AppData\Local\Python\pythoncore-3.14-64\Scripts\streamlit.exe

echo 왼쪽/오른쪽 여백에 사진을 넣을 수 있습니다!
echo 사진 이름: photo1.jpg, photo2.jpg, photo3.jpg, photo4.jpg
echo website_deploy 폴더에 넣어주세요.
echo 다시 실행합니다...
"%STREAMLIT_EXE%" run app.py
pause
