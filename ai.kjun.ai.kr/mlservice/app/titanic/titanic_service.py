import pandas as pd
import numpy as np
from sklearn import datasets
from icecream import ic
import os
from typing import Optional, List, Dict, Any
from titanic.titanic_method import TitanicMethod


class PassengerService:
    """Titanic Passenger CRUD 서비스"""
    
    def __init__(self):
        pass

    def preprocess(self) -> Dict[str, Any]:
        ic("🦝🦝전처리 시작")
        the_method = TitanicMethod()
        df_train = the_method.new_model('train.csv')
        df_test = the_method.new_model('test.csv')
        this_train = the_method.create_train(df_train, 'Survived')
        this_test = the_method.create_train(df_test, 'Survived')
        ic(f'1. Train 의 type \n {type(this_train)} ')
        ic(f'2. Train 의 type \n {type(this_train)} ')
        ic(f'3. Train 의 column \n {this_train.columns} ')
        ic(f'4. Train 의 상위 5개 행\n {this_train.head(5)} ')
        ic(f'5. Train 의 null 의 갯수\n {the_method.check_null(this_train)}개')
        #ic(f'6. Test 의 type \n {type(this_test)}')
        #ic(f'7. Test 의 column \n {this_test.columns}')
        #ic(f'8. Test 의 상위 1개 행\n {this_test.head()}개')
        #ic(f'9. Test 의 null 의 갯수\n {this_test.isnull().sum()}개')
        
        drop_features = ['SibSp', 'Parch', 'Cabin', 'Ticket']
        this_train = the_method.drop_feature(this_train, *drop_features)
        this_train = the_method.pclass_ordinal(this_train)
        this_train = the_method.title_nominal(this_train)
        this_train = the_method.gender_nominal(this_train)
        this_train = the_method.age_ratio(this_train)
        this_train = the_method.fare_ordinal(this_train)
        this_train = the_method.embarked_ordinal(this_train)
        drop_name = ['Name']
        this_train = the_method.drop_feature(this_train, *drop_name)

        ic("🦝🦝전처리 완료")
        ic(f'1. Train 의 type \n {type(this_train)} ')
        ic(f'2. Train 의 type \n {type(this_train)} ')
        ic(f'3. Train 의 column \n {this_train.columns} ')
        ic(f'4. Train 의 상위 5개 행\n {this_train.head(5)} ')
        ic(f'5. Train 의 null 의 갯수\n {the_method.check_null(this_train)}개')

        
        # JSON 응답을 위한 데이터 변환
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
        
        def df_to_dict(df, head_rows=5):
            head_data = df.head(head_rows).to_dict(orient='records')
            return {
                "head": clean_dict(head_data),
                "columns": df.columns.tolist(),
                "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
                "null_counts": {col: int(count) for col, count in df.isnull().sum().items()}
            }
        
        return {
            "message": "전처리 완료",
            "train": df_to_dict(this_train),
            "test": df_to_dict(this_test),
            "train_type": str(type(this_train)),
            "test_type": str(type(this_test))
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