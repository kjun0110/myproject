import logging
import pandas as pd
import numpy as np
from pandas import DataFrame
from pathlib import Path
from seoullab_crime.seoullab_data import SeoullabData





logger = logging.getLogger(__name__)


class SeoullabMethod(object):

    def __init__(self):
        #데이터셋 객체 생성
        self.dataset = SeoullabData()
        # data 폴더의 절대 경로
        self.data_path = Path(__file__).resolve().parent / "data"

    def read_csv(self, fname: str) -> pd.DataFrame:
        #csv 파일을 읽어와서 데이터프레임으로 반환
        filepath = self.data_path / fname
        if not filepath.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")
        return pd.read_csv(filepath)

    def read_excel(self, fname: str) -> pd.DataFrame:
        #xlsx/xls 파일을 읽어와서 데이터프레임으로 반환
        filepath = self.data_path / fname
        if not filepath.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")
        
        # 파일 확장자에 따라 엔진 선택
        file_ext = filepath.suffix.lower()
        engine = 'xlrd' if file_ext == '.xls' else 'openpyxl'
        
        # 일반 Excel 파일 읽기
        try:
            return pd.read_excel(filepath, engine=engine)
        except ImportError:
            raise ImportError(f"{engine} 패키지가 필요합니다. 'pip install {engine}'을 실행해주세요.")

    def csv_to_df(self, fname: str) -> pd.DataFrame:
        #csv 파일을 읽어와서 데이터셋 객체에 저장(데이터 프레임 작성)
        return self.read_csv(fname)
        
    def xlsx_to_df(self, fname: str) -> pd.DataFrame:
        #xlsx 파일을 읽어와서 데이터셋 객체에 저장(데이터 프레임 작성)
        return self.read_excel(fname)


    def create_df(self, df: DataFrame, label: str) -> pd.DataFrame:
        #Survived 값을 제거한 데이터프레임 작성
        # train_df는 label 컬럼이 있으므로 제거, test_df는 label 컬럼이 없을 수 있으므로 확인 후 제거
        return self.dataset.create_df(df, label)

    def df_merge(self, right: pd.DataFrame, left: pd.DataFrame, left_on: str, right_on: str, how: str = 'left', keep_key: str = 'right') -> pd.DataFrame:
        """
        두 데이터프레임을 머지
        
        Args:
            right: 오른쪽 데이터프레임 (기준이 되는 데이터프레임)
            left: 왼쪽 데이터프레임 (병합할 데이터프레임)
            left_on: 왼쪽 데이터프레임의 키 컬럼명
            right_on: 오른쪽 데이터프레임의 키 컬럼명
            how: 머지 방식 ('left', 'right', 'inner', 'outer')
            keep_key: 머지 후 유지할 키 컬럼 ('right', 'left', 또는 둘 다 'both')
        
        Returns:
            머지된 데이터프레임
        """
        # 중복된 컬럼 확인 및 제거 (키 컬럼 제외)
        left_cols = set(left.columns) - {left_on}
        right_cols = set(right.columns) - {right_on}
        
        # 중복된 컬럼이 있으면 왼쪽 데이터프레임에서 제거
        overlap_cols = left_cols & right_cols
        if overlap_cols:
            logger.warning(f"중복된 컬럼이 발견되어 왼쪽 데이터프레임에서 제거합니다: {overlap_cols}")
            left = left.drop(columns=list(overlap_cols))
        
        # 머지 수행
        merged_df = pd.merge(
            right, 
            left, 
            left_on=right_on, 
            right_on=left_on, 
            how=how,
            suffixes=('', '_duplicate')  # 중복 방지용 접미사 (사실상 사용되지 않음)
        )
        
        # 접미사가 붙은 중복 컬럼 제거
        duplicate_cols = [col for col in merged_df.columns if col.endswith('_duplicate')]
        if duplicate_cols:
            merged_df = merged_df.drop(columns=duplicate_cols)
        
        # 키 컬럼 중복 제거 처리
        if keep_key == 'right':
            # 오른쪽 키 컬럼 유지, 왼쪽 키 컬럼 제거
            if left_on in merged_df.columns:
                merged_df = merged_df.drop(columns=[left_on])
        elif keep_key == 'left':
            # 왼쪽 키 컬럼 유지, 오른쪽 키 컬럼 제거
            if right_on in merged_df.columns:
                merged_df = merged_df.drop(columns=[right_on])
            # 왼쪽 키 컬럼명은 그대로 유지 (자치구)
        # keep_key == 'both'인 경우 둘 다 유지
        
        return merged_df
