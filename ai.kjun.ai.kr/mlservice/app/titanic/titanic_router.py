from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from .titanic_service import TitanicService
import logging

logger = logging.getLogger(__name__)

titanic_router = APIRouter(prefix="/titanic", tags=["titanic"])

# TitanicService 인스턴스
service = TitanicService()


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
        logger.error(f"전처리 오류 발생: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@titanic_router.get("/evaluate")
async def evaluate_model():
    """
    모델 평가 실행 
    실행 후 모델 평가 결과 반환
    """
    try:
        # 전처리, 모델링, 학습, 평가 순서로 실행
        service.preprocess()
        service.modeling()
        service.learning()
        result = service.evaluate()
        
        return JSONResponse(content={
            "success": True,
            "data": result
        })
    except Exception as e:
        import traceback
        logger.error(f"평가 오류 발생: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@titanic_router.get("/submit")
@titanic_router.post("/submit")
async def submit_model(model_name: str = Query(default=None, description="사용할 모델 이름 (None이면 정확도가 가장 높은 모델 자동 선택)")):
    """
    Kaggle 제출 파일 생성
    모델명을 선택하여 제출 파일을 생성합니다.
    model_name이 None이면 정확도가 가장 높은 모델을 자동으로 선택합니다.
    
    Args:
        model_name: 사용할 모델 이름 (None이면 자동 선택, 기본값: None)
                    'logistic_regression', 'naive_bayes', 'random_forest', 'lightgbm', 'svm'
    
    Example:
        GET /api/ml/titanic/submit (자동 선택)
        GET /api/ml/titanic/submit?model_name=lightgbm (특정 모델 선택)
        POST /api/ml/titanic/submit (자동 선택)
        POST /api/ml/titanic/submit?model_name=lightgbm (특정 모델 선택)
    """
    try:
        # 전처리, 모델링, 학습 순서로 실행
        service.preprocess()
        service.modeling()
        service.learning()
        
        # 제출 파일 생성 (model_name이 None이면 자동으로 정확도가 가장 높은 모델 선택)
        result = service.submit(model_name=model_name)
        
        return JSONResponse(content={
            "success": True,
            "data": result
        })
    except Exception as e:
        import traceback
        logger.error(f"제출 파일 생성 오류 발생: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
