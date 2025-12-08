from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from .titanic_service import PassengerService
from icecream import ic

titanic_router = APIRouter(prefix="/titanic", tags=["titanic"])

# PassengerService 인스턴스
service = PassengerService()


@titanic_router.get("/")
async def root():
    """Titanic API 루트"""
    return {"message": "Titanic Passenger API"}


@titanic_router.get("/preprocess")
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

