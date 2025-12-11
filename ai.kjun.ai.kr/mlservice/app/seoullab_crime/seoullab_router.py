from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from .seoullab_service import SeoullabService
import logging

logger = logging.getLogger(__name__)

seoullab_router = APIRouter(prefix="/seoullab", tags=["seoullab"])

# SeoullabService 인스턴스
service = SeoullabService()


@seoullab_router.get("/")
async def root():
    """Seoul Crime API 루트"""
    return {"message": "Seoul Crime API"}


@seoullab_router.get("/preprocess")
async def preprocess():
    """전처리 수행 및 결과 조회"""
    try:
        result = service.preprocess()
        return JSONResponse(content={
            "success": True,
            "data": result
        })
    except FileNotFoundError as e:
        import traceback
        error_msg = f"파일을 찾을 수 없습니다: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=404, detail=error_msg)
    except ImportError as e:
        import traceback
        error_msg = f"필요한 패키지가 설치되지 않았습니다: {str(e)}. openpyxl을 설치해주세요: pip install openpyxl"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        import traceback
        error_msg = f"전처리 오류 발생: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)


@seoullab_router.get("/preprocess/{data_type}")
async def get_preprocess_data(data_type: str):
    """
    특정 타입의 전처리 데이터만 조회
    
    Args:
        data_type: 'cctv', 'crime', 'pop', 'crime_with_gu' 중 하나
    
    Example:
        GET /seoullab/preprocess/cctv
        GET /seoullab/preprocess/crime
        GET /seoullab/preprocess/pop
        GET /seoullab/preprocess/crime_with_gu
    """
    try:
        result = service.get_data_by_type(data_type)
        return JSONResponse(content={
            "success": True,
            "data_type": data_type,
            "data": result
        })
    except ValueError as e:
        logger.error(f"데이터 타입 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(f"데이터 조회 오류 발생: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

