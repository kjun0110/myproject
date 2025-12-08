from titanic.titanic_dataset import TitanicDataSet
import pandas as pd
import numpy as np
import os
from pandas import DataFrame
from icecream import ic


class TitanicMethod(object):

    def __init__(self):
        #데이터셋 객체 생성
        self.dataset = TitanicDataSet()


    def new_model(self, fname: str) -> pd.DataFrame:
        #train.csv 파일을 읽어와서 데이터셋 객체에 저장(데이터 프레임 작성)
        # 경로 설정은 TitanicDataSet 객체를 통해 처리
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

    def pclass_ordinal(self, df: DataFrame) -> pd.DataFrame:
        """
        Pclass: 객실 등급 (1, 2, 3)
        - 서열형 척도(ordinal)로 처리합니다.
        - 1등석 > 2등석 > 3등석이므로, 생존률 관점에서 1이 가장 좋고 3이 가장 안 좋습니다.
        - Pclass는 이미 1,2,3으로 인코딩되어 있으므로 그대로 사용합니다.

        """
        # Pclass가 이미 ordinal 형태이므로 그대로 사용
        # 필요시 역순 변환도 가능: df['Pclass_ordinal'] = 4 - df['Pclass']
        df = df.copy()
        df['Pclass'] = df['Pclass'].astype(int)
        return df
    
    def title_nominal(self, df: DataFrame) -> pd.DataFrame:
        """
        Title: 명칭 (Mr, Mrs, Miss, Master, Dr, etc.)
        - Name 컬럼에서 추출한 타이틀입니다.
        - nominal 척도입니다.
        - Label Encoding으로 정수형으로 변환합니다.
        - Mr=0, Miss=1, Mrs=2, Master=3, Rare=4
        """
        # Name에서 Title 추출: "Braund, Mr. Owen Harris" -> "Mr"
        if 'Name' in df.columns:
            df['Title'] = df['Name'].str.extract(r',\s*([^.]+)\.', expand=False)
            df['Title'] = df['Title'].str.strip()
            
            # 희소한 타이틀을 "Rare" 그룹으로 묶기
            title_mapping = {
                'Mr': 'Mr',
                'Miss': 'Miss',
                'Mrs': 'Mrs',  
                'Master': 'Master',
                'Dr': 'Rare',
                'Rev': 'Rare',
                'Col': 'Rare',
                'Major': 'Rare',
                'Mlle': 'Miss',  # Mademoiselle
                'Mme': 'Mrs',     # Madame
                'Don': 'Rare',
                'Lady': 'Rare',
                'Countess': 'Rare',
                'Jonkheer': 'Rare',
                'Sir': 'Rare',
                'Capt': 'Rare',
                'Ms': 'Miss',
                'Dona': 'Rare'
            }
            
            # 매핑되지 않은 타이틀은 'Rare'로 처리
            df['Title'] = df['Title'].map(title_mapping).fillna('Rare')
            
            # Label Encoding으로 정수형 변환
            # Mr=0, Miss=1, Mrs=2, Master=3, Rare=4
            df['Title'] = df['Title'].map({'Mr': 0, 'Miss': 1, 'Mrs': 2, 'Master': 3, 'Rare': 4}).astype(int)
            
        return df
    
    def gender_nominal(self, df: DataFrame) -> pd.DataFrame:
        """
        Sex: 성별 (male, female)
        - nominal 척도입니다.
        - Label Encoding으로 숫자형으로 변환합니다.
        - male=0, female=1
        """
        if 'Sex' in df.columns:
            # Label Encoding으로 숫자형 변환
            # male=0, female=1
            df['Gender'] = df['Sex'].map({'male': 0, 'female': 1}).astype(int)
            
            # 원본 Sex 컬럼 삭제
            df = df.drop(columns=['Sex'])
        
        return df

    def age_ratio(self, df: DataFrame) -> pd.DataFrame:
        """
        Age: 나이
        - 원래는 ratio 척도지만, 나이를 구간으로 나눈 ordinal 피처를 만듭니다.
        - bins: [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
          의미: Unknown(0), Baby(1), Child(2), Teenager(3), Student(4), Young Adult(5), Adult(6), Senior(7)
        """
        if 'Age' in df.columns:
            bins = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
            
            # Age를 숫자형으로 변환 (문자열이 섞여있을 수 있음)
            df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
            
            # 결측치를 중앙값으로 채우기
            age_median = df['Age'].median()
            df['Age'] = df['Age'].fillna(age_median)
            
            # 나이를 구간화하여 ordinal 인코딩 (정수형으로 변환)
            df['Age'] = pd.cut(df['Age'], bins=bins, labels=False, include_lowest=True).astype(int)
            
        return df

    def fare_ordinal(self, df: DataFrame) -> pd.DataFrame:
        """
        Fare: 요금
        - 연속형 ratio 척도이지만, 구간화하여 서열형으로 사용합니다.
        - 결측치는 중앙값으로 채웁니다.
        - 사분위수로 binning하여 ordinal 피처를 만듭니다.
        """
        if 'Fare' in df.columns:
            # Fare를 숫자형으로 변환 (문자열이 섞여있을 수 있음)
            df['Fare'] = pd.to_numeric(df['Fare'], errors='coerce')
            
            # 결측치를 중앙값으로 채우기
            fare_median = df['Fare'].median()
            df['Fare'] = df['Fare'].fillna(fare_median)
            
            # 0보다 작은 값 처리 (있을 경우)
            df['Fare'] = df['Fare'].clip(lower=0)
            
            # 사분위수로 binning하여 ordinal 인코딩 (숫자로 변환)
            try:
                df['Fare'] = pd.qcut(df['Fare'], q=4, labels=False, duplicates='drop')
            except ValueError:
                # 중복값이 많아 qcut이 실패할 경우 cut 사용
                fare_bins = [df['Fare'].min() - 1, df['Fare'].quantile(0.25), 
                            df['Fare'].quantile(0.5), df['Fare'].quantile(0.75), df['Fare'].max() + 1]
                df['Fare'] = pd.cut(df['Fare'], bins=fare_bins, labels=False, include_lowest=True)
            
        return df

    def embarked_ordinal(self, df: DataFrame) -> pd.DataFrame:
        """
        Embarked: 탑승 항구 (C, Q, S)
        - 본질적으로는 nominal(명목) 척도입니다.
        - Label Encoding으로 정수형으로 변환합니다.
        - C=0, Q=1, S=2
        """
        if 'Embarked' in df.columns:
            # 결측치를 가장 많이 등장하는 값(mode)으로 채우기
            embarked_mode = df['Embarked'].mode()
            if len(embarked_mode) > 0:
                df['Embarked'] = df['Embarked'].fillna(embarked_mode[0])
            else:
                # mode가 없으면 'S'로 채우기 (가장 일반적인 값)
                df['Embarked'] = df['Embarked'].fillna('S')
            
            # Label Encoding으로 정수형 변환
            # C=0, Q=1, S=2
            df['Embarked'] = df['Embarked'].map({'C': 0, 'Q': 1, 'S': 2}).astype(int)
            
        return df