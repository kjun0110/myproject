import logging
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, Any

logger = logging.getLogger(__name__)


class KoElectraService:
    """KoElectra 모델을 사용한 감정 분석 서비스"""
    
    def __init__(self):
        """서비스 초기화 및 모델 로드"""
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = Path(__file__).parent / "koelectra_model"
        self._load_model()
    
    def _load_model(self):
        """KoElectra 모델과 토크나이저 로드"""
        try:
            logger.info(f"KoElectra 모델 로드 시작: {self.model_path}")
            
            # 모델 경로 확인
            if not self.model_path.exists():
                raise FileNotFoundError(f"모델 경로를 찾을 수 없습니다: {self.model_path}")
            
            # 토크나이저 로드
            self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
            logger.info("토크나이저 로드 완료")
            
            # 모델 로드
            self.model = AutoModelForSequenceClassification.from_pretrained(str(self.model_path))
            self.model.to(self.device)
            self.model.eval()  # 평가 모드로 설정
            logger.info(f"모델 로드 완료 (device: {self.device})")
            
        except Exception as e:
            logger.error(f"모델 로드 중 오류 발생: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        문장의 감정을 분석합니다.
        
        Args:
            text: 분석할 문장
        
        Returns:
            dict: 감정 분석 결과
                - sentiment: 감정 레이블 (positive, negative, neutral 등)
                - confidence: 신뢰도 (0.0 ~ 1.0)
                - scores: 각 감정별 점수
        """
        if not text or not text.strip():
            return {
                "success": False,
                "error": "입력 문장이 비어있습니다."
            }
        
        try:
            logger.info(f"감정 분석 시작: {text[:50]}...")
            
            # 텍스트 토크나이징
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            
            # 모델에 입력
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
            
            # 소프트맥스로 확률 변환
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            probabilities = probabilities.cpu().numpy()[0]
            
            # 감정 레이블 (모델에 따라 다를 수 있음)
            # 일반적으로: 0=negative, 1=neutral, 2=positive 또는 0=negative, 1=positive
            # 실제 모델의 레이블에 맞게 조정 필요
            sentiment_labels = ["negative", "neutral", "positive"]
            
            # 가장 높은 확률의 감정 찾기
            predicted_class = probabilities.argmax()
            confidence = float(probabilities[predicted_class])
            
            # 레이블 수에 맞게 조정
            if len(probabilities) == 2:
                sentiment_labels = ["negative", "positive"]
            elif len(probabilities) > 3:
                sentiment_labels = [f"label_{i}" for i in range(len(probabilities))]
            
            predicted_sentiment = sentiment_labels[predicted_class] if predicted_class < len(sentiment_labels) else f"label_{predicted_class}"
            
            # 각 감정별 점수 생성
            scores = {}
            for i, label in enumerate(sentiment_labels[:len(probabilities)]):
                scores[label] = float(probabilities[i])
            
            result = {
                "success": True,
                "text": text,
                "sentiment": predicted_sentiment,
                "confidence": round(confidence, 4),
                "scores": scores
            }
            
            logger.info(f"감정 분석 완료: {predicted_sentiment} (신뢰도: {confidence:.4f})")
            return result
            
        except Exception as e:
            logger.error(f"감정 분석 중 오류 발생: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }

