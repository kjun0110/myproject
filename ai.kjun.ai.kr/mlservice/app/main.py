from fastapi import FastAPI
from titanic.titanic_router import titanic_router
from grade.grade_router import grade_router
from seoul_crime.seoul_router import seoul_router
from seoullab_crime.seoullab_router import seoullab_router
from us_unemployment.router import usa_router
from nlp.nlp_router import nlp_router
import logging
from dotenv import load_dotenv
import os
from pathlib import Path

# Logging 설정 (먼저 설정)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 콘솔 출력
    ]
)

# .env 파일 로드 (상위 디렉토리부터 순차적으로 찾기)
env_paths = [
    Path(__file__).parent.parent.parent / '.env',  # /app/../.env
    Path(__file__).parent.parent / '.env',          # /app/.env
    Path(__file__).parent / '.env'                  # /app/app/.env
]

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logging.info(f".env 파일 로드 완료: {env_path}")
        env_loaded = True
        break

if not env_loaded:
    load_dotenv()  # 기본 경로에서도 시도
    logging.warning("기본 경로에서 .env 파일을 찾지 못했습니다. docker-compose 환경변수를 사용합니다.")

# 환경변수 확인
if os.getenv('KAKAO_REST_API_KEY'):
    logging.info("KAKAO_REST_API_KEY 환경변수 로드 성공")
else:
    logging.warning("KAKAO_REST_API_KEY 환경변수를 찾을 수 없습니다.")

app = FastAPI(
    title="ML Service",
    description="Machine Learning 서비스",
    version="1.0.0",
)

# CORS는 게이트웨이에서 처리하므로 여기서는 설정하지 않음

# Titanic 라우터 연결
app.include_router(titanic_router)

# Grade 라우터 연결
app.include_router(grade_router)

# Seoul Crime 라우터 연결
app.include_router(seoul_router)

# Seoullab Crime 라우터 연결
app.include_router(seoullab_router)

# USA Unemployment 라우터 연결
app.include_router(usa_router)

# NLP 라우터 연결
app.include_router(nlp_router)

@app.get("/")
async def root():
    return {"message": "ML Service API"}
