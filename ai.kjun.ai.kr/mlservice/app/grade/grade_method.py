from grade.grade_dataset import GradeDataSet
import pandas as pd
import numpy as np
import os
from pandas import DataFrame
from icecream import ic


class GradeMethod(object):

    def __init__(self):
        #데이터셋 객체 생성
        self.dataset = GradeDataSet()


    def new_model(self, fname: str) -> pd.DataFrame:
        #train.csv 파일을 읽어와서 데이터셋 객체에 저장(데이터 프레임 작성)
        # 경로 설정은 GradeDataSet 객체를 통해 처리
        csv_path = self.dataset.get_csv_path(fname)
        return pd.read_csv(csv_path)

    def create_train(self, df: DataFrame, label: str) -> pd.DataFrame:
        #Survived 값을 제거한 데이터프레임 작성
        if label in df.columns:
            return df.drop(columns=[label])
        return df  # 컬럼이 없으면 그대로 반환 (test.csv의 경우)

    def create_label(self, df: DataFrame, label: str) -> pd.DataFrame:
        #servived 값만 가지는 답안지 데이터프레임 작성
        return df[[label]]

    def drop_feature(self, df: DataFrame, *features:str) -> pd.DataFrame:
        #피쳐를 삭제하는 메소드
        return df.drop(columns=[x for x in features])

    
    def check_null(self, df: DataFrame) -> int:
        ic('데이터 결측치 확인')
        return int(df.isnull().sum().sum())


    # 척도 : nominal ordinal interval ratio    


    def esg_rating_ordinal(self, df: DataFrame) -> pd.DataFrame:
        """
        ESG_Rating: ESG 통합 등급 (S, A+, A, B+, B, C, D)
        - 서열형 척도(ordinal)로 처리합니다.
        - S(탁월) > A+(매우 우수) > A(우수) > B+(양호) > B(보통) > C(취약) > D(매우 취약)
        - Label Encoding으로 정수형으로 변환합니다.
        - S=6, A+=5, A=4, B+=3, B=2, C=1, D=0
        """
        if 'esg_rating' in df.columns:
            # 결측치 처리 (최빈값 또는 'C'로 채우기)
            esg_mode = df['esg_rating'].mode()
            if len(esg_mode) > 0:
                df['esg_rating'] = df['esg_rating'].fillna(esg_mode[0])
            else:
                df['esg_rating'] = df['esg_rating'].fillna('C')  # 기본값: 보통
            
            # Label Encoding으로 정수형 변환
            # S=6 (최고), A+=5, A=4, B+=3, B=2, C=1, D=0 (최하)
            rating_mapping = {
                'S': 6,
                'A+': 5,
                'A': 4,
                'B+': 3,
                'B': 2,
                'C': 1,
                'D': 0
            }
            df['esg_rating'] = df['esg_rating'].map(rating_mapping).fillna(1).astype(int)  # 매핑 실패 시 C(1)로 처리
        
        return df

    def env_rating_ordinal(self, df: DataFrame) -> pd.DataFrame:
        """
        ENV_Rating: 환경 등급 (S, A+, A, B+, B, C, D)
        - 서열형 척도(ordinal)로 처리합니다.
        - ESG와 동일한 7개 등급 체계
        - S=6, A+=5, A=4, B+=3, B=2, C=1, D=0
        """
        if 'env_rating' in df.columns:
            # 결측치 처리 (최빈값 또는 'C'로 채우기)
            env_mode = df['env_rating'].mode()
            if len(env_mode) > 0:
                df['env_rating'] = df['env_rating'].fillna(env_mode[0])
            else:
                df['env_rating'] = df['env_rating'].fillna('C')
            
            # Label Encoding으로 정수형 변환
            rating_mapping = {
                'S': 6,
                'A+': 5,
                'A': 4,
                'B+': 3,
                'B': 2,
                'C': 1,
                'D': 0
            }
            df['env_rating'] = df['env_rating'].map(rating_mapping).fillna(1).astype(int)
        
        return df

    def soc_rating_ordinal(self, df: DataFrame) -> pd.DataFrame:
        """
        SOC_Rating: 사회 등급 (S, A+, A, B+, B, C, D)
        - 서열형 척도(ordinal)로 처리합니다.
        - ESG와 동일한 7개 등급 체계
        - S=6, A+=5, A=4, B+=3, B=2, C=1, D=0
        """
        if 'soc_rating' in df.columns:
            # 결측치 처리 (최빈값 또는 'C'로 채우기)
            soc_mode = df['soc_rating'].mode()
            if len(soc_mode) > 0:
                df['soc_rating'] = df['soc_rating'].fillna(soc_mode[0])
            else:
                df['soc_rating'] = df['soc_rating'].fillna('C')
            
            # Label Encoding으로 정수형 변환
            rating_mapping = {
                'S': 6,
                'A+': 5,
                'A': 4,
                'B+': 3,
                'B': 2,
                'C': 1,
                'D': 0
            }
            df['soc_rating'] = df['soc_rating'].map(rating_mapping).fillna(1).astype(int)
        
        return df

    def gov_rating_ordinal(self, df: DataFrame) -> pd.DataFrame:
        """
        GOV_Rating: 지배구조 등급 (S, A+, A, B+, B, C, D)
        - 서열형 척도(ordinal)로 처리합니다.
        - ESG와 동일한 7개 등급 체계
        - S=6, A+=5, A=4, B+=3, B=2, C=1, D=0
        """
        if 'gov_rating' in df.columns:
            # 결측치 처리 (최빈값 또는 'C'로 채우기)
            gov_mode = df['gov_rating'].mode()
            if len(gov_mode) > 0:
                df['gov_rating'] = df['gov_rating'].fillna(gov_mode[0])
            else:
                df['gov_rating'] = df['gov_rating'].fillna('C')
            
            # Label Encoding으로 정수형 변환
            rating_mapping = {
                'S': 6,
                'A+': 5,
                'A': 4,
                'B+': 3,
                'B': 2,
                'C': 1,
                'D': 0
            }
            df['gov_rating'] = df['gov_rating'].map(rating_mapping).fillna(1).astype(int)
        
        return df

    def year_ordinal(self, df: DataFrame) -> pd.DataFrame:
        """
        Year: 연도
        - 현재는 2025년만 있지만 향후 추가될 수 있습니다.
        - 정수형으로 변환합니다.
        
        전략 옵션:
        1. 그대로 사용: 2025, 2026, 2027... (권장)
        2. 최소 연도 기준 상대값: 2025=0, 2026=1, 2027=2...
        
        여기서는 옵션 1을 사용합니다 (연도 그대로 사용).
        """
        if 'year' in df.columns:
            # 연도를 정수형으로 변환
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
            
            # 결측치 처리 (현재 연도로 채우기)
            current_year = 2025  # 또는 df['year'].mode()[0]
            df['year'] = df['year'].fillna(current_year).astype(int)
        
        return df