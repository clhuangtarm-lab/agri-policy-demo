FROM python:3.11-slim

WORKDIR /app

# 系統套件（pandas 需要 libgomp1）
RUN apt-get update && apt-get install -y --no-install-recommends \
      libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 先裝 Python 套件以利 layer 快取
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案（含已建置的 data/demo.db）
COPY . .

# 若沒有 data/demo.db，在 build 階段嘗試跑 ETL
# （部署前請先在本地跑完 ETL，把 demo.db 一併放進映像檔）
RUN python -c "import os,sys; sys.exit(0 if os.path.exists('data/demo.db') and os.path.getsize('data/demo.db')>1000000 else 1)" \
    || echo "警告：data/demo.db 不存在或為空，部署後會找不到資料。請先在本機執行 python -m etl.build_db。"

ENV PYTHONUNBUFFERED=1
ENV DATABASE_PATH=/app/data/demo.db

EXPOSE 8080

# Zeabur / Render 會注入 PORT，也接受 8080 預設
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
