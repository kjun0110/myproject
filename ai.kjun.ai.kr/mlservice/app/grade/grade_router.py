from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from .grade_service import GradeService
from icecream import ic

grade_router = APIRouter(prefix="/grade", tags=["grade"])

# GradeService 인스턴스
service = GradeService()


@grade_router.get("/")
async def root():
    """Grade API 루트"""
    return {"message": "Grade API"}


@grade_router.get("/preprocess")
async def preprocess():
    """전처리 수행 및 결과 조회"""
    try:
        result = service.preprocess()
        return JSONResponse(content={
            "success": True,
            "data": result
        })
    except Exception as e:
        import traceback
        ic(f"전처리 오류 발생: {e}")
        ic(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

