import os
import requests

class KakaoMapSingleton:
    _instance = None  # 싱글턴 인스턴스를 저장할 클래스 변수

    def __new__(cls):
        if cls._instance is None:  # 인스턴스가 없으면 생성
            cls._instance = super(KakaoMapSingleton, cls).__new__(cls)
            cls._instance._api_key = cls._instance._retrieve_api_key()  # API 키 가져오기
            cls._instance._base_url = "https://dapi.kakao.com/v2/local"
        return cls._instance  # 기존 인스턴스 반환

    def _retrieve_api_key(self):
        """API 키를 가져오는 내부 메서드"""
        api_key = os.getenv('KAKAO_REST_API_KEY')
        if not api_key:
            raise ValueError("KAKAO_REST_API_KEY 환경변수가 설정되지 않았습니다.")
        return api_key

    def get_api_key(self):
        """저장된 API 키 반환"""
        return self._api_key

    def geocode(self, address, language='ko'):
        """주소를 위도, 경도로 변환하는 메서드 (카카오 맵 API)"""
        import logging
        logger = logging.getLogger(__name__)
        
        # 키워드 검색 API 사용 (장소명 검색용)
        url = f"{self._base_url}/search/keyword.json"
        headers = {
            "Authorization": f"KakaoAK {self._api_key}"
        }
        params = {
            "query": address
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            # 에러 응답 처리
            if response.status_code == 403:
                error_msg = response.json().get('message', 'Forbidden')
                logger.error(f"카카오 맵 API 403 에러: {error_msg}")
                logger.error(f"요청 URL: {url}")
                logger.error(f"요청 주소: {address}")
                raise ValueError(f"카카오 맵 API 접근 거부 (403): {error_msg}. 카카오 개발자 콘솔에서 '로컬' API가 활성화되어 있는지 확인하세요.")
            
            response.raise_for_status()  # HTTP 에러 발생 시 예외 발생
            
            result = response.json()
            
            # Google Maps API와 유사한 형식으로 변환
            if result.get('documents') and len(result['documents']) > 0:
                doc = result['documents'][0]
                # 키워드 검색 결과는 place_name, address_name, road_address_name 등을 포함
                address_name = doc.get('address_name', '') or doc.get('road_address_name', '')
                return [{
                    "formatted_address": address_name,
                    "geometry": {
                        "location": {
                            "lat": float(doc.get('y', 0)),
                            "lng": float(doc.get('x', 0))
                        }
                    }
                }]
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"카카오 맵 API 요청 실패: {e}")
            raise

