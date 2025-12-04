from fastapi import FastAPI, APIRouter
import uvicorn
import sys
from pathlib import Path

# 현재 파일의 디렉토리를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from bd_demo.bugsmusic import crawl_bugs_chart
from bd_demo.danawa import crawl_danawa_products
from sel_demo.navernews import crawl_navernews

app = FastAPI(
    title="Crawler Service API",
    description="Crawler Service API for the application",
    version="1.0.0",
)

# 서브 라우터 생성
crawler_router = APIRouter(prefix="/crawler", tags=["crawler"])

@crawler_router.get("/")
async def crawler_root():
    return {"message": "Crawler Service"}

@crawler_router.get("/bugsmusic")
async def get_bugs_chart():
    """
    Bugs Music 실시간 차트를 크롤링하여 반환합니다.
    
    Returns:
        dict: 크롤링 결과 (success, count, data)
    """
    chart_data = crawl_bugs_chart()
    return {
        "success": True,
        "count": len(chart_data),
        "data": chart_data
    }

@crawler_router.get("/danawa")
async def get_danawa_products():
    """
    다나와 메탈시계 제품 정보를 크롤링하여 반환합니다.
    
    Returns:
        dict: 크롤링 결과 (success, count, data)
    """
    products_data = crawl_danawa_products()
    return {
        "success": True,
        "count": len(products_data),
        "data": products_data
    }

@crawler_router.get("/navernews")
async def get_navernews():
    """
    네이버 뉴스 검색 결과를 크롤링하여 반환합니다. (키워드: ESG, 기간: 전체)
    
    Returns:
        dict: 크롤링 결과 (success, count, data)
    """
    news_data = crawl_navernews("esg")
    return {
        "success": True,
        "count": len(news_data),
        "data": news_data
    }


# 서브 라우터를 앱에 포함
app.include_router(crawler_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9002)

