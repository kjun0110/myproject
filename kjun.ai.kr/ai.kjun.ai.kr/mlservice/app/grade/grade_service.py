import pandas as pd
import numpy as np
from sklearn import datasets
from icecream import ic
import os
from typing import Optional, List, Dict, Any
from grade.grade_method import GradeMethod
import math


class GradeService:
    """ESG 등급 데이터 서비스"""
    
    def __init__(self):
        pass

    def preprocess(self) -> Dict[str, Any]:
        ic("🦝🦝전처리 시작")
        the_method = GradeMethod()
        df_grade = the_method.new_model('grade.csv')
        this_grade = the_method.create_train(df_grade, 'esg_rating')
        ic(f'1. Grade 의 type \n {type(this_grade)} ')
        ic(f'2. Grade 의 column \n {this_grade.columns} ')
        ic(f'3. Grade 의 상위 5개 행\n {this_grade.head(5)} ')
        ic(f'4. Grade 의 null 의 갯수\n {the_method.check_null(this_grade)}개')
        
        drop_features = ['NO', 'company_name']
        this_grade = the_method.drop_feature(this_grade, *drop_features)
        this_grade = the_method.env_rating_ordinal(this_grade)
        this_grade = the_method.soc_rating_ordinal(this_grade)
        this_grade = the_method.gov_rating_ordinal(this_grade)
        this_grade = the_method.year_ordinal(this_grade)

        ic("🦝🦝전처리 완료")
        ic(f'전처리 후 column \n {this_grade.columns} ')
        ic(f'전처리 후 상위 5개 행\n {this_grade.head(5)} ')
        ic(f'전처리 후 null 의 갯수\n {the_method.check_null(this_grade)}개')
        
        # JSON 응답을 위한 데이터 변환
        def safe_convert(value):
            if pd.isna(value):
                return None
            if isinstance(value, (np.integer, np.floating)):
                if math.isnan(value) or math.isinf(value):
                    return None
                return float(value) if isinstance(value, np.floating) else int(value)
            return value
        
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(elem) for elem in d]
            else:
                return safe_convert(d)
        
        def df_to_dict(df, head_rows=5):
            return {
                "head": clean_dict(df.head(head_rows).to_dict(orient='records')),
                "columns": df.columns.tolist(),
                "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
                "null_counts": {col: int(count) for col, count in df.isnull().sum().items()}
            }
        
        return {
            "message": "전처리 완료",
            "grade": df_to_dict(this_grade),
            "grade_type": str(type(this_grade))
        }

    def modeling(self):
        ic("🦝🦝모델링 시작")
        ic("🦝🦝모델링 완료")

    def learning(self):
        ic("🦝🦝학습 시작")
        ic("🦝🦝학습 완료")

    def postprocess(self):
        ic("🦝🦝후처리 시작")
        ic("🦝🦝후처리 완료")


    def submit(self):
        ic("🦝🦝제출 시작")
        ic("🦝🦝제출 완료")