from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
import io
import logging
from PIL import Image
from pathlib import Path
from .emma.emma_wordcloud import NLPService
from .samsung.samsung_wordcloud import SamsungWordcloud

logger = logging.getLogger(__name__)

nlp_router = APIRouter(prefix="/nlp", tags=["nlp"])

# NLPService 인스턴스 생성
nlp_service = NLPService()

# SamsungWordcloud 인스턴스는 필요할 때 생성 (초기화 오류 방지)
samsung_wordcloud = None

def get_samsung_wordcloud():
    """SamsungWordcloud 인스턴스를 지연 초기화"""
    global samsung_wordcloud
    if samsung_wordcloud is None:
        try:
            samsung_wordcloud = SamsungWordcloud()
        except Exception as e:
            logger.error(f"SamsungWordcloud 초기화 실패: {str(e)}")
            raise
    return samsung_wordcloud


@nlp_router.get("/")
async def root():
    """NLP API 루트"""
    return {"message": "NLP Service API"}


@nlp_router.get("/emma")
async def generate_emma_wordcloud(
    width: Optional[int] = Query(1000, description="이미지 너비"),
    height: Optional[int] = Query(600, description="이미지 높이"),
    background_color: Optional[str] = Query("white", description="배경색"),
    random_state: Optional[int] = Query(0, description="랜덤 시드")
):
    """
    엠마 말뭉치를 기반으로 워드클라우드 생성
    
    Args:
        width: 이미지 너비 (기본값: 1000)
        height: 이미지 높이 (기본값: 600)
        background_color: 배경색 (기본값: white)
        random_state: 랜덤 시드 (기본값: 0)
        
    Returns:
        StreamingResponse: PNG 이미지 스트림
    """
    try:
        # 엠마 말뭉치 로드
        logger.info("엠마 말뭉치 로드 중...")
        emma_raw = nlp_service.get_emma_corpus()
        
        if not emma_raw:
            raise HTTPException(
                status_code=404, 
                detail="엠마 말뭉치를 찾을 수 없습니다."
            )
        
        # 고유명사 추출 및 빈도 분포 생성
        logger.info("고유명사 추출 중...")
        proper_nouns_fd = nlp_service.extract_proper_nouns(emma_raw)
        
        if not proper_nouns_fd or len(proper_nouns_fd) == 0:
            raise HTTPException(
                status_code=500,
                detail="고유명사를 추출할 수 없습니다."
            )
        
        # 워드클라우드 생성 (저장하지 않음)
        logger.info("워드클라우드 생성 중...")
        wordcloud, saved_path = nlp_service.generate_wordcloud(
            freq_dist=proper_nouns_fd,
            width=width,
            height=height,
            background_color=background_color,
            random_state=random_state,
            save_path=None  # 저장하지 않음
        )
        
        # WordCloud 객체를 이미지로 변환
        # WordCloud는 to_array() 메서드로 numpy 배열을 반환
        wordcloud_array = wordcloud.to_array()
        
        # numpy 배열을 PIL Image로 변환
        img = Image.fromarray(wordcloud_array)
        
        # 이미지를 바이트 스트림으로 변환
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        logger.info("워드클라우드 생성 완료")
        
        # 이미지 스트림 반환
        return StreamingResponse(
            img_buffer,
            media_type="image/png",
            headers={
                "Content-Disposition": "attachment; filename=emma_wordcloud.png"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"워드클라우드 생성 오류: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)


@nlp_router.get("/emma/save")
async def save_emma_wordcloud(
    width: Optional[int] = Query(1000, description="이미지 너비"),
    height: Optional[int] = Query(600, description="이미지 높이"),
    background_color: Optional[str] = Query("white", description="배경색"),
    random_state: Optional[int] = Query(0, description="랜덤 시드")
):
    """
    엠마 말뭉치를 기반으로 워드클라우드 생성 및 저장
    
    Args:
        width: 이미지 너비 (기본값: 1000)
        height: 이미지 높이 (기본값: 600)
        background_color: 배경색 (기본값: white)
        random_state: 랜덤 시드 (기본값: 0)
        
    Returns:
        JSONResponse: 저장된 파일 경로 정보
    """
    try:
        # 엠마 말뭉치 로드
        logger.info("엠마 말뭉치 로드 중...")
        emma_raw = nlp_service.get_emma_corpus()
        
        if not emma_raw:
            raise HTTPException(
                status_code=404, 
                detail="엠마 말뭉치를 찾을 수 없습니다."
            )
        
        # 고유명사 추출 및 빈도 분포 생성
        logger.info("고유명사 추출 중...")
        proper_nouns_fd = nlp_service.extract_proper_nouns(emma_raw)
        
        if not proper_nouns_fd or len(proper_nouns_fd) == 0:
            raise HTTPException(
                status_code=500,
                detail="고유명사를 추출할 수 없습니다."
            )
        
        # 워드클라우드 생성 및 저장 (고정 파일명으로 덮어쓰기)
        logger.info("워드클라우드 생성 및 저장 중...")
        wordcloud, saved_path = nlp_service.generate_wordcloud(
            freq_dist=proper_nouns_fd,
            width=width,
            height=height,
            background_color=background_color,
            random_state=random_state,
            save_path="fixed"  # 고정 파일명으로 덮어쓰기
        )
        
        logger.info(f"워드클라우드 이미지 저장 완료: {saved_path}")
        
        # 저장된 파일 정보 반환
        from pathlib import Path
        saved_path_obj = Path(saved_path)
        
        return JSONResponse(content={
            "success": True,
            "message": "워드클라우드 이미지가 성공적으로 저장되었습니다.",
            "data": {
                "file_path": saved_path,
                "file_name": saved_path_obj.name,
                "directory": str(saved_path_obj.parent),
                "width": width,
                "height": height,
                "background_color": background_color,
                "random_state": random_state
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"워드클라우드 저장 오류: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)


@nlp_router.get("/emma/stats")
async def get_emma_stats():
    """
    엠마 말뭉치 통계 정보 조회
    
    Returns:
        dict: 통계 정보
    """
    try:
        # 엠마 말뭉치 로드
        emma_raw = nlp_service.get_emma_corpus()
        
        if not emma_raw:
            raise HTTPException(
                status_code=404,
                detail="엠마 말뭉치를 찾을 수 없습니다."
            )
        
        # 고유명사 추출
        proper_nouns_fd = nlp_service.extract_proper_nouns(emma_raw)
        
        # 통계 정보
        total_count = proper_nouns_fd.N()
        most_common = nlp_service.get_most_common(proper_nouns_fd, 10)
        
        # Emma 단어 통계
        emma_stats = nlp_service.get_freq_stats(proper_nouns_fd, "Emma")
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "total_proper_nouns": total_count,
                "unique_proper_nouns": len(proper_nouns_fd),
                "emma_stats": {
                    "count": emma_stats[1],
                    "frequency": emma_stats[2]
                },
                "most_common": [
                    {"word": word, "count": count}
                    for word, count in most_common
                ]
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"통계 조회 오류: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)


@nlp_router.get("/samsung/save")
async def save_samsung_wordcloud():
    """
    삼성 리포트를 기반으로 워드클라우드 생성 및 저장
    
    Returns:
        JSONResponse: 저장된 파일 경로 정보
    """
    try:
        logger.info("삼성 워드클라우드 생성 및 저장 시작...")
        
        # SamsungWordcloud 인스턴스 가져오기 (지연 초기화)
        swc = get_samsung_wordcloud()
        
        # 워드클라우드 생성 및 저장
        output_file_path = swc.draw_wordcloud()
        
        # 저장된 파일 경로 확인
        output_file = Path(output_file_path)
        
        if not output_file.exists():
            raise HTTPException(
                status_code=500,
                detail=f"워드클라우드 파일이 생성되지 않았습니다: {output_file_path}"
            )
        
        logger.info(f"삼성 워드클라우드 이미지 저장 완료: {output_file}")
        
        return JSONResponse(content={
            "success": True,
            "message": "워드클라우드 이미지가 성공적으로 저장되었습니다.",
            "data": {
                "file_path": str(output_file),
                "file_name": output_file.name,
                "directory": str(output_file.parent)
            }
        })
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        error_msg = f"필요한 파일을 찾을 수 없습니다: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)
    except ImportError as e:
        error_msg = f"필요한 라이브러리가 설치되지 않았습니다: {str(e)}. pip install konlpy를 실행하세요."
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        import traceback
        error_msg = f"삼성 워드클라우드 저장 오류: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

