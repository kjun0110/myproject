from titanic.titanic_dataset import TitanicDataSet
from typing import Tuple
import pandas as pd
import numpy as np
from pandas import DataFrame
import os
import logging


logger = logging.getLogger(__name__)


class TitanicMethod(object):

    def __init__(self):
        #데이터셋 객체 생성
        self.dataset = TitanicDataSet()

    def read_csv(self, fname: str) -> pd.DataFrame:
        #train.csv 파일을 읽어와서 데이터셋 객체에 저장(데이터 프레임 작성)
        # 경로 설정은 TitanicDataSet 객체를 통해 처리
        return self.dataset.read_csv(fname)

    def create_df(self, df: DataFrame, label: str) -> pd.DataFrame:
        #Survived 값을 제거한 데이터프레임 작성
        # train_df는 label 컬럼이 있으므로 제거, test_df는 label 컬럼이 없을 수 있으므로 확인 후 제거
        return self.dataset.create_df(df, label)

    def create_label(self, df: DataFrame, label: str) -> pd.DataFrame:
        #servived 값만 가지는 답안지 데이터프레임 작성
        return self.dataset.create_label(df, label)

    def drop_feature(self, this, *features: str) -> object:
        #피쳐를 삭제하는 메소드
        return [this.drop_feature(*features) for _ in [1]][0]

    def check_null(self, this) -> None:
        [this.check_null() for _ in [1]]

    # 척도 : nominal ordinal interval ratio    

    def pclass_ordinal(self, this) -> object:
        """
        Pclass: 객실 등급 (1, 2, 3)
        - 서열형 척도(ordinal)로 처리합니다.
        - 1등석 > 2등석 > 3등석이므로, 생존률 관점에서 1이 가장 좋고 3이 가장 안 좋습니다.
        - Pclass는 이미 1,2,3으로 인코딩되어 있으므로 그대로 사용합니다.
        """
        return [this.pclass_ordinal() for _ in [1]][0]

    def title_nominal(self, this) -> object:
        """
        Title: 명칭 (Mr, Mrs, Miss, Master, Dr, etc.)
        - Name 컬럼에서 추출한 타이틀입니다.
        - nominal 척도입니다.
        - Label Encoding으로 정수형으로 변환합니다.
        - Mr=0, Miss=1, Mrs=2, Master=3, Rare=4
        """
        return [this.title_nominal() for _ in [1]][0]

    def gender_nominal(self, this) -> object:
        """
        Sex: 성별 (male, female)
        - nominal 척도입니다.
        - Label Encoding으로 숫자형으로 변환합니다.
        - male=0, female=1
        """
        return [this.gender_nominal() for _ in [1]][0]

    def age_ratio(self, this) -> object:
        """
        Age: 나이
        - 원래는 ratio 척도지만, 나이를 구간으로 나눈 ordinal 피처를 만듭니다.
        - bins: [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
          의미: Unknown(0), Baby(1), Child(2), Teenager(3), Student(4), Young Adult(5), Adult(6), Senior(7)
        """
        return [this.age_ratio() for _ in [1]][0]

    def fare_ordinal(self, this) -> object:
        """
        Fare: 요금
        - 연속형 ratio 척도이지만, 구간화하여 서열형으로 사용합니다.
        - 결측치는 중앙값으로 채웁니다.
        - 사분위수로 binning하여 ordinal 피처를 만듭니다.
        """
        return [this.fare_ordinal() for _ in [1]][0]

    def embarked_ordinal(self, this) -> object:
        """
        Embarked: 탑승 항구 (C, Q, S)
        - 본질적으로는 nominal(명목) 척도입니다.
        - Label Encoding으로 정수형으로 변환합니다.
        - C=0, Q=1, S=2
        """
        return [this.embarked_ordinal() for _ in [1]][0]