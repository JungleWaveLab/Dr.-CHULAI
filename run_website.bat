@echo off
chcp 65001 > nul
set PYTHONUTF8=1

REM Find streamlit executable
set STREAMLIT_EXE=C:\Users\hdy73\AppData\Local\Python\pythoncore-3.14-64\Scripts\streamlit.exe

echo 다크모드를 기본으로 설정했습니다!
echo 우측 상단 버튼으로 모드를 바꿀 수 있습니다.
echo 다시 실행합니다...
"%STREAMLIT_EXE%" run app.py
pause
