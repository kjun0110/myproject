from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import importlib.util
from pathlib import Path

# 프로젝트 루트 경로 설정
project_root = Path(__file__).parent.parent.parent
crawler_main_path = project_root / "services" / "crawlerservice" / "app" / "main.py"

# crawler-service의 라우터 동적 import
spec = importlib.util.spec_from_file_location("crawler_main", crawler_main_path)
crawler_main = importlib.util.module_from_spec(spec)
sys.modules["crawler_main"] = crawler_main
spec.loader.exec_module(crawler_main)
crawler_router = crawler_main.crawler_router

app = FastAPI(
    title="Gateway API",
    description="Gateway API for the application",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 origin만 허용하도록 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 메인 라우터 생성
main_router = APIRouter()

@main_router.get("/")
async def root():
    return {"message": "안녕 파이썬"}

# 메인 라우터를 앱에 포함
app.include_router(main_router)

# crawler-service 서브 라우터를 앱에 직접 포함
app.include_router(crawler_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)

