import sys
import pandas as pd
import numpy as np
import logging
from seoul_crime.seoul_method import SeoulMethod

logger = logging.getLogger(__name__)

class SeoulService:

    def __init__(self):
        self.method = SeoulMethod()

    def preprocess(self):
        logger.info("🦝🦝전처리 시작")
        
        try:
            # 각 파일을 읽어서 데이터프레임으로 변환
            logger.info("CCTV 파일 읽기 시작...")
            cctv_df = self.method.xlsx_to_df('cctv.xlsx')
            logger.info(f"CCTV 파일 읽기 완료: {cctv_df.shape}")
            
            logger.info("Crime 파일 읽기 시작...")
            crime_df = self.method.csv_to_df('crime.csv')
            logger.info(f"Crime 파일 읽기 완료: {crime_df.shape}")
            
            logger.info("Pop 파일 읽기 시작...")
            pop_df = self.method.csv_to_df('pop.csv')
            logger.info(f"Pop 파일 읽기 완료: {pop_df.shape}")
        except FileNotFoundError as e:
            logger.error(f"파일을 찾을 수 없습니다: {e}")
            raise
        except Exception as e:
            logger.error(f"파일 읽기 중 오류 발생: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        # 데이터셋 객체에 저장
        self.method.dataset.cctv = cctv_df
        self.method.dataset.crime = crime_df
        self.method.dataset.pop = pop_df
        
        logger.info(f"CCTV 데이터: {cctv_df.shape}")
        logger.info(f"Crime 데이터: {crime_df.shape}")
        logger.info(f"Pop 데이터: {pop_df.shape}")
        logger.info("🦝🦝전처리 완료")
        
        # 각 데이터프레임의 상위 5개 행을 반환
        import math
        def safe_convert(value):
            """NaN, inf 값을 JSON 호환 값으로 변환"""
            if pd.isna(value):
                return None
            if isinstance(value, (np.integer, np.floating)):
                if math.isnan(value) or math.isinf(value):
                    return None
                return float(value) if isinstance(value, np.floating) else int(value)
            return value
        
        def clean_dict(d):
            """딕셔너리의 모든 값을 안전하게 변환"""
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(item) for item in d]
            else:
                return safe_convert(d)
        
        def df_to_dict(df, head_rows=5, skip_rows=0):
            """
            데이터프레임을 딕셔너리로 변환
            
            Args:
                df: 데이터프레임
                head_rows: 표시할 행 수
                skip_rows: 건너뛸 행 수 (스키마 행 등)
            """
            # skip_rows 이후부터 head_rows만큼 가져오기
            if skip_rows > 0:
                head_data = df.iloc[skip_rows:skip_rows+head_rows].to_dict(orient='records')
            else:
                head_data = df.head(head_rows).to_dict(orient='records')
            return {
                "head": clean_dict(head_data),
                "columns": df.columns.tolist(),
                "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
                "null_counts": {col: int(count) for col, count in df.isnull().sum().items()}
            }
        
        cctv_pop = self.method.df_merge(cctv, pop, 'id')

        return {
            "message": "전처리 완료",
            "cctv": df_to_dict(cctv_df),
            "crime": df_to_dict(crime_df),  # 다중 헤더 처리로 인해 첫 행부터 데이터
            "pop": df_to_dict(pop_df)
        }

    def modeling(self):
        logger.info("🦝🦝모델링 시작")
        logger.info("🦝🦝모델링 완료")

    def learning(self):
        logger.info("🦝🦝학습 시작")
        logger.info("🦝🦝학습 완료")

    def evaluate(self):
        logger.info("🦝🦝평가 시작")
        logger.info("🦝🦝평가 완료")

    def postprocess(self):
        logger.info("🦝🦝후처리 시작")
        logger.info("🦝🦝후처리 완료")

    def submit(self):
        pass

    def get_data_by_type(self, data_type: str):
        """
        특정 타입의 데이터만 반환
        
        Args:
            data_type: 'cctv', 'crime', 'pop' 중 하나
        
        Returns:
            해당 데이터프레임의 상위 5개 행 정보
        """
        # 먼저 전처리를 실행하여 데이터를 로드
        if self.method.dataset.cctv is None or self.method.dataset.crime is None or self.method.dataset.pop is None:
            logger.info("데이터가 로드되지 않았습니다. 전처리를 실행합니다.")
            self.preprocess()
        
        import math
        def safe_convert(value):
            """NaN, inf 값을 JSON 호환 값으로 변환"""
            if pd.isna(value):
                return None
            if isinstance(value, (np.integer, np.floating)):
                if math.isnan(value) or math.isinf(value):
                    return None
                return float(value) if isinstance(value, np.floating) else int(value)
            return value
        
        def clean_dict(d):
            """딕셔너리의 모든 값을 안전하게 변환"""
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(item) for item in d]
            else:
                return safe_convert(d)
        
        def df_to_dict(df, head_rows=5, skip_rows=0):
            """
            데이터프레임을 딕셔너리로 변환
            
            Args:
                df: 데이터프레임
                head_rows: 표시할 행 수
                skip_rows: 건너뛸 행 수 (스키마 행 등)
            """
            # skip_rows 이후부터 head_rows만큼 가져오기
            if skip_rows > 0:
                head_data = df.iloc[skip_rows:skip_rows+head_rows].to_dict(orient='records')
            else:
                head_data = df.head(head_rows).to_dict(orient='records')
            return {
                "head": clean_dict(head_data),
                "columns": df.columns.tolist(),
                "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
                "null_counts": {col: int(count) for col, count in df.isnull().sum().items()}
            }
        
        # 타입에 따라 해당 데이터프레임 반환
        if data_type.lower() == 'cctv':
            df = self.method.dataset.cctv
            if df is None:
                raise ValueError(f"{data_type} 데이터가 로드되지 않았습니다.")
            return df_to_dict(df)
        elif data_type.lower() == 'crime':
            df = self.method.dataset.crime
            if df is None:
                raise ValueError(f"{data_type} 데이터가 로드되지 않았습니다.")
            return df_to_dict(df)  # 다중 헤더 처리로 인해 첫 행부터 데이터
        elif data_type.lower() == 'pop':
            df = self.method.dataset.pop
            if df is None:
                raise ValueError(f"{data_type} 데이터가 로드되지 않았습니다.")
            return df_to_dict(df)
        else:
            raise ValueError(f"지원하지 않는 데이터 타입입니다: {data_type}. 'cctv', 'crime', 'pop' 중 하나를 선택하세요.")