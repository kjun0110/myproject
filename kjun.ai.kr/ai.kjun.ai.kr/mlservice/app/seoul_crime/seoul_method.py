import logging
import pandas as pd
import numpy as np
from pandas import DataFrame
from seoul_crime.seoul_data import SeoulData





logger = logging.getLogger(__name__)


class SeoulMethod(object):

    def __init__(self):
        #데이터셋 객체 생성
        self.dataset = SeoulData()


    def csv_to_df(self, fname: str) -> pd.DataFrame:
        #csv 파일을 읽어와서 데이터셋 객체에 저장(데이터 프레임 작성)
        # 경로 설정은 seoulData 객체를 통해 처리
        return self.dataset.read_csv(fname)
        
    def xlsx_to_df(self, fname: str) -> pd.DataFrame:
        #xlsx 파일을 읽어와서 데이터셋 객체에 저장(데이터 프레임 작성)
        # 경로 설정은 seoulData 객체를 통해 처리
        return self.dataset.read_excel(fname)


    def create_df(self, df: DataFrame, label: str) -> pd.DataFrame:
        #Survived 값을 제거한 데이터프레임 작성
        # train_df는 label 컬럼이 있으므로 제거, test_df는 label 컬럼이 없을 수 있으므로 확인 후 제거
        return self.dataset.create_df(df, label)

    def df_merge(self, right:pd.DataFrame, left:pd.DataFrame, feature: str) -> pd.DataFrame:
        return pd.merge(right, left, on=feature, how='left')
