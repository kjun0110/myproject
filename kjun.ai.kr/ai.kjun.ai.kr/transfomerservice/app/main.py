from fastapi import FastAPI
import sys
from pathlib import Path

# app 디렉토리를 Python path에 추가
app_dir = Path(__file__).parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from koelectra.koelectra_router import koelectra_router
import logging

# Logging 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 콘솔 출력
    ]
)

app = FastAPI(
    title="Transformer Service",
    description="Transformer 기반 NLP 서비스",
    version="1.0.0",
)

# KoElectra 라우터 연결
app.include_router(koelectra_router)

@app.get("/")
async def root():
    return {"message": "Transformer Service API"}

