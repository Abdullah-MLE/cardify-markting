uv init


uv venv .venv


.\.venv\Scripts\Activate.ps1


uv pip install -r requirements.txt


uv pip freeze > requirements.txt


ngrok http 127.0.0.1:8000


uvicorn main:app --reload --port 8000
