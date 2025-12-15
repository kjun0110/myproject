from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
from .koelectra_service import KoElectraService
import logging

logger = logging.getLogger(__name__)

koelectra_router = APIRouter(prefix="/koelectra", tags=["koelectra"])

# KoElectraService 인스턴스 (지연 로딩)
service = None

def get_service():
    """서비스 인스턴스를 지연 로딩으로 가져옵니다"""
    global service
    if service is None:
        service = KoElectraService()
    return service


class SentimentRequest(BaseModel):
    """감정 분석 요청 모델"""
    text: str


class SentimentScores(BaseModel):
    """감정별 점수"""
    negative: float = None
    neutral: float = None
    positive: float = None


class SentimentAnalysisResult(BaseModel):
    """감정 분석 결과"""
    success: bool
    text: str
    sentiment: str
    confidence: float
    scores: Dict[str, float]


class SentimentResponse(BaseModel):
    """감정 분석 API 응답"""
    success: bool
    data: SentimentAnalysisResult


@koelectra_router.get("/")
async def root():
    """KoElectra API 루트"""
    return {"message": "KoElectra Sentiment Analysis API"}


@koelectra_router.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """
    문장의 감정을 분석합니다.
    
    Args:
        request: 감정 분석 요청 (text 필드 포함)
    
    Returns:
        SentimentResponse: 감정 분석 결과
    """
    try:
        service_instance = get_service()
        result = service_instance.analyze_sentiment(request.text)
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "감정 분석 실패"))
        
        # Pydantic 모델로 변환
        sentiment_result = SentimentAnalysisResult(**result)
        return SentimentResponse(success=True, data=sentiment_result)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"감정 분석 오류 발생: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)


@koelectra_router.get("/analyze", response_model=SentimentResponse)
async def analyze_sentiment_get(text: str):
    """
    GET 방식으로 문장의 감정을 분석합니다.
    
    Args:
        text: 분석할 문장 (쿼리 파라미터)
    
    Returns:
        SentimentResponse: 감정 분석 결과
    """
    try:
        service_instance = get_service()
        result = service_instance.analyze_sentiment(text)
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "감정 분석 실패"))
        
        # Pydantic 모델로 변환
        sentiment_result = SentimentAnalysisResult(**result)
        return SentimentResponse(success=True, data=sentiment_result)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"감정 분석 오류 발생: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

