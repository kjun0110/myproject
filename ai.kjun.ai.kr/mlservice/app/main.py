from fastapi import FastAPI
from titanic.titanic_router import titanic_router
from grade.grade_router import grade_router

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

@app.get("/")
async def root():
    return {"message": "ML Service API"}
