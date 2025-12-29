# FastAPI 엔트리 + 정적 파일 서빙(/outputs/...)
# + 라우팅 등록입니다.
import sys
from pathlib import Path

# 현재 디렉토리를 sys.path에 추가 (uvicorn 직접 실행 시 패키지 컨텍스트 보장)
_current_dir = Path(__file__).parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# 절대 임포트 시도, 실패하면 상대 임포트 사용
try:
    from api.v1.routes.generate import router as generate_router
    from core.config import OUTPUTS_DIR
except ImportError:
    from .api.v1.routes.generate import router as generate_router
    from .core.config import OUTPUTS_DIR

app = FastAPI(title="Diffusers API", version="1.0.0")

# outputs 정적 서빙 (로컬 개발/단독 서버에서 편리)
# OUTPUTS_DIR은 config.py에서 이미 생성되지만, 추가로 확인
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

app.include_router(generate_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"ok": True}
