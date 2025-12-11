import requests
import pandas as pd
import folium
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class UnemploymentService:
    """미국 실업률 데이터를 시각화하는 서비스 클래스"""
    
    def __init__(self):
        """서비스 초기화"""
        self.state_geo_url = "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"
        self.state_data_url = "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_unemployment_oct_2012.csv"
        self.state_geo = None
        self.state_data = None
        self.map = None
    
    def load_geo_data(self) -> dict:
        """
        미국 주별 지리 데이터를 로드합니다.
        
        Returns:
            dict: 주별 지리 데이터 (GeoJSON)
        """
        try:
            logger.info("지리 데이터 로드 시작...")
            response = requests.get(self.state_geo_url)
            response.raise_for_status()
            self.state_geo = response.json()
            logger.info("지리 데이터 로드 완료")
            return self.state_geo
        except requests.exceptions.RequestException as e:
            logger.error(f"지리 데이터 로드 실패: {e}")
            raise
    
    def load_unemployment_data(self) -> pd.DataFrame:
        """
        미국 실업률 데이터를 로드합니다.
        
        Returns:
            pd.DataFrame: 실업률 데이터프레임
        """
        try:
            logger.info("실업률 데이터 로드 시작...")
            self.state_data = pd.read_csv(self.state_data_url)
            logger.info(f"실업률 데이터 로드 완료: {self.state_data.shape}")
            return self.state_data
        except Exception as e:
            logger.error(f"실업률 데이터 로드 실패: {e}")
            raise
    
    def create_map(
        self,
        location: list = [48, -102],
        zoom_start: int = 3,
        fill_color: str = "YlGn",
        fill_opacity: float = 0.7,
        line_opacity: float = 0.2
    ) -> folium.Map:
        """
        실업률 데이터를 시각화한 지도를 생성합니다.
        
        Args:
            location: 지도의 중심 좌표 [위도, 경도]
            zoom_start: 초기 줌 레벨
            fill_color: 색상 팔레트
            fill_opacity: 채우기 투명도
            line_opacity: 선 투명도
        
        Returns:
            folium.Map: 생성된 지도 객체
        """
        try:
            logger.info("지도 생성 시작...")
            
            # 데이터 로드 (아직 로드되지 않은 경우)
            if self.state_geo is None:
                self.load_geo_data()
            if self.state_data is None:
                self.load_unemployment_data()
            
            # 지도 생성
            self.map = folium.Map(location=location, zoom_start=zoom_start)
            
            # Choropleth 레이어 추가
            folium.Choropleth(
                geo_data=self.state_geo,
                name="choropleth",
                data=self.state_data,
                columns=["State", "Unemployment"],
                key_on="feature.id",
                fill_color=fill_color,
                fill_opacity=fill_opacity,
                line_opacity=line_opacity,
                legend_name="Unemployment Rate (%)",
            ).add_to(self.map)
            
            # 레이어 컨트롤 추가
            folium.LayerControl().add_to(self.map)
            
            logger.info("지도 생성 완료")
            return self.map
            
        except Exception as e:
            logger.error(f"지도 생성 중 오류 발생: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def save_map(self, file_path: str) -> str:
        """
        생성된 지도를 HTML 파일로 저장합니다.
        
        Args:
            file_path: 저장할 파일 경로
        
        Returns:
            str: 저장된 파일 경로
        """
        if self.map is None:
            raise ValueError("지도가 생성되지 않았습니다. create_map()을 먼저 호출하세요.")
        
        try:
            logger.info(f"지도 저장 시작: {file_path}")
            self.map.save(file_path)
            logger.info(f"지도 저장 완료: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"지도 저장 중 오류 발생: {e}")
            raise
    
    def get_map_html(self) -> str:
        """
        생성된 지도의 HTML 문자열을 반환합니다.
        
        Returns:
            str: 지도의 HTML 문자열
        """
        if self.map is None:
            raise ValueError("지도가 생성되지 않았습니다. create_map()을 먼저 호출하세요.")
        
        return self.map._repr_html_()
