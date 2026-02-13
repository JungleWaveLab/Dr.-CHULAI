@echo off
chcp 65001 > nul
set PYTHONUTF8=1

REM Find streamlit executable
set STREAMLIT_EXE=C:\Users\hdy73\AppData\Local\Python\pythoncore-3.14-64\Scripts\streamlit.exe

echo 배경 이미지가 있으면 자동으로 적용됩니다!
echo 다시 실행합니다...
"%STREAMLIT_EXE%" run app.py
pause
