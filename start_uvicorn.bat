@echo off
REM Activate the virtual environment
call .\venv\Scripts\activate

REM Start the Uvicorn server
start cmd /k uvicorn backend.endpoints:app --reload --port 8001

REM Start the Streamlit app
start cmd /k streamlit run Chatbot.py