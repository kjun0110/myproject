from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from .service import UnemploymentService
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

usa_router = APIRouter(prefix="/usa", tags=["usa"])

# UnemploymentService 인스턴스
service = UnemploymentService()


@usa_router.get("/")
async def root():
    """USA Unemployment API 루트"""
    return {"message": "USA Unemployment API"}


@usa_router.get("/map", response_class=HTMLResponse)
async def get_map():
    """
    미국 실업률 지도를 생성하고 HTML로 반환합니다.
    
    Returns:
        HTMLResponse: 지도 HTML
    """
    try:
        map_obj = service.create_map()
        html_content = service.get_map_html()
        return HTMLResponse(content=html_content)
    except Exception as e:
        import traceback
        error_msg = f"지도 생성 오류 발생: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)


@usa_router.get("/map/save")
async def save_map():
    """
    미국 실업률 지도를 생성하고 파일로 저장합니다.
    
    Returns:
        dict: 저장 결과
    """
    try:
        # 지도 생성
        map_obj = service.create_map()
        
        # 저장 경로 설정: ai.kjun.ai.kr/mlservice/app/us_unemployment/save
        save_path = Path(__file__).parent / "save"
        save_path.mkdir(exist_ok=True)
        file_path = save_path / "unemployment_map.html"
        
        # 파일 저장
        saved_path = service.save_map(str(file_path))
        
        return JSONResponse(content={
            "success": True,
            "message": "지도 저장 완료",
            "file_path": str(saved_path)
        })
    except Exception as e:
        import traceback
        error_msg = f"지도 저장 오류 발생: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)


@usa_router.get("/data")
async def get_data():
    """
    미국 실업률 데이터를 조회합니다.
    
    Returns:
        dict: 실업률 데이터
    """
    try:
        # 데이터 로드
        geo_data = service.load_geo_data()
        unemployment_data = service.load_unemployment_data()
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "unemployment": unemployment_data.to_dict(orient='records'),
                "geo_data_available": geo_data is not None
            }
        })
    except Exception as e:
        import traceback
        error_msg = f"데이터 조회 오류 발생: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

