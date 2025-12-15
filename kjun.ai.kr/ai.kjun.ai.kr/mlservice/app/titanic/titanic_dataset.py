from dataclasses import dataclass
import pandas as pd
import numpy as np
import os
import logging
from pandas import DataFrame

logger = logging.getLogger(__name__)

@dataclass
class TitanicDataSet(object):
    _fname: str = ''  # file name
    _dname: str = ''  # data path
    _sname: str = ''  # save path
    _train: pd.DataFrame = None
    _test: pd.DataFrame = None
    _id: str = ''
    _label: str = ''

    @property
    def fname(self) -> str:
        return self._fname

    @fname.setter
    def fname(self, fname):
        self._fname = fname

    @property
    def dname(self) -> str:
        return self._dname

    @dname.setter
    def dname(self, dname):
        self._dname = dname

    @property
    def sname(self) -> str:
        return self._sname

    @sname.setter
    def sname(self, sname):
        self._sname = sname

    @property
    def train(self) -> object:
        return self._train

    @train.setter
    def train(self, train):
        self._train = train

    @property
    def test(self) -> object:
        return self._test

    @test.setter
    def test(self, test):
        self._test = test

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    def read_csv(self, fname: str) -> pd.DataFrame:
        #train.csv 파일을 읽어와서 데이터셋 객체에 저장(데이터 프레임 작성)
        # 경로 설정은 TitanicDataSet 객체를 통해 처리
        return pd.read_csv(fname)

    def create_df(self, df: DataFrame, label: str) -> pd.DataFrame:
        #Survived 값을 제거한 데이터프레임 작성
        # train_df는 label 컬럼이 있으므로 제거, test_df는 label 컬럼이 없을 수 있으므로 확인 후 제거
        if label in df.columns:
            return df.drop(columns=[label])
        return df

    def create_label(self, df: DataFrame, label: str) -> pd.DataFrame:
        #servived 값만 가지는 답안지 데이터프레임 작성
        return df[[label]]

    def drop_feature(self, *features: str) -> object:
        #피쳐를 삭제하는 메소드
        [i.drop(j, axis=1, inplace=True) for j in features for i in [self.train, self.test]]
        return self

    def check_null(self) -> None:
        [logger.info(f"Null counts: {i.isnull().sum()}") for i in [self.train, self.test]]
        for i in [self.train, self.test]:
            logger.info("🦝🦝🦝")
            logger.info(f"Null counts: {i.isnull().sum()}")

    def pclass_ordinal(self) -> object:
        """
        Pclass: 객실 등급 (1, 2, 3)
        - 서열형 척도(ordinal)로 처리합니다.
        - 1등석 > 2등석 > 3등석이므로, 생존률 관점에서 1이 가장 좋고 3이 가장 안 좋습니다.
        - Pclass는 이미 1,2,3으로 인코딩되어 있으므로 그대로 사용합니다.
        """
        # Pclass가 이미 ordinal 형태이므로 그대로 사용
        # 필요시 역순 변환도 가능: df['Pclass_ordinal'] = 4 - df['Pclass']
        if 'Pclass' in self.train.columns and 'Pclass' in self.test.columns:
            [df.update(pd.DataFrame({'Pclass': df['Pclass'].astype(int)}, index=df.index)) for df in [self.train, self.test]]
        return self

    def title_nominal(self) -> object:
        """
        Title: 명칭 (Mr, Mrs, Miss, Master, Dr, etc.)
        - Name 컬럼에서 추출한 타이틀입니다.
        - nominal 척도입니다.
        - Label Encoding으로 정수형으로 변환합니다.
        - Mr=0, Miss=1, Mrs=2, Master=3, Rare=4
        """
        if 'Name' in self.train.columns and 'Name' in self.test.columns:
            title_mapping = {
                'Mr': 'Mr', 'Miss': 'Miss', 'Mrs': 'Mrs', 'Master': 'Master',
                'Dr': 'Rare', 'Rev': 'Rare', 'Col': 'Rare', 'Major': 'Rare',
                'Mlle': 'Miss', 'Mme': 'Mrs', 'Don': 'Rare', 'Lady': 'Rare',
                'Countess': 'Rare', 'Jonkheer': 'Rare', 'Sir': 'Rare', 'Capt': 'Rare',
                'Ms': 'Miss', 'Dona': 'Rare'
            }
            label_mapping = {'Mr': 0, 'Miss': 1, 'Mrs': 2, 'Master': 3, 'Rare': 4}
            
            for df in [self.train, self.test]:
                df['Title'] = df['Name'].str.extract(r',\s*([^.]+)\.', expand=False).str.strip()
                df['Title'] = df['Title'].map(title_mapping).fillna('Rare')
                df['Title'] = df['Title'].map(label_mapping).astype(int)
        return self

    def gender_nominal(self) -> object:
        """
        Sex: 성별 (male, female)
        - nominal 척도입니다.
        - Label Encoding으로 숫자형으로 변환합니다.
        - male=0, female=1
        """
        if 'Sex' in self.train.columns and 'Sex' in self.test.columns:
            for df in [self.train, self.test]:
                df['Gender'] = df['Sex'].map({'male': 0, 'female': 1}).astype(int)
                df.drop(columns=['Sex'], inplace=True)
        return self

    def age_ratio(self) -> object:
        """
        Age: 나이
        - 원래는 ratio 척도지만, 나이를 구간으로 나눈 ordinal 피처를 만듭니다.
        - bins: [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
          의미: Unknown(0), Baby(1), Child(2), Teenager(3), Student(4), Young Adult(5), Adult(6), Senior(7)
        """
        if 'Age' in self.train.columns and 'Age' in self.test.columns:
            bins = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
            age_median = self.train['Age'].median()
            for df in [self.train, self.test]:
                df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
                df['Age'] = df['Age'].fillna(age_median)
                df['Age'] = pd.cut(df['Age'], bins=bins, labels=False, include_lowest=True).astype(int)
        return self

    def fare_ordinal(self) -> object:
        """
        Fare: 요금
        - 연속형 ratio 척도이지만, 구간화하여 서열형으로 사용합니다.
        - 결측치는 중앙값으로 채웁니다.
        - 사분위수로 binning하여 ordinal 피처를 만듭니다.
        """
        if 'Fare' in self.train.columns and 'Fare' in self.test.columns:
            fare_median = self.train['Fare'].median()
            for df in [self.train, self.test]:
                df['Fare'] = pd.to_numeric(df['Fare'], errors='coerce')
                df['Fare'] = df['Fare'].fillna(fare_median)
                df['Fare'] = df['Fare'].clip(lower=0)
            try:
                for df in [self.train, self.test]:
                    df['Fare'] = pd.qcut(df['Fare'], q=4, labels=False, duplicates='drop').astype(int)
            except ValueError:
                fare_bins = [self.train['Fare'].min() - 1, self.train['Fare'].quantile(0.25), 
                            self.train['Fare'].quantile(0.5), self.train['Fare'].quantile(0.75), self.train['Fare'].max() + 1]
                for df in [self.train, self.test]:
                    df['Fare'] = pd.cut(df['Fare'], bins=fare_bins, labels=False, include_lowest=True).astype(int)
        return self

    def embarked_ordinal(self) -> object:
        """
        Embarked: 탑승 항구 (C, Q, S)
        - 본질적으로는 nominal(명목) 척도입니다.
        - Label Encoding으로 정수형으로 변환합니다.
        - C=0, Q=1, S=2
        """
        if 'Embarked' in self.train.columns and 'Embarked' in self.test.columns:
            embarked_mode = self.train['Embarked'].mode()
            fill_value = embarked_mode[0] if len(embarked_mode) > 0 else 'S'
            for df in [self.train, self.test]:
                df['Embarked'] = df['Embarked'].fillna(fill_value).map({'C': 0, 'Q': 1, 'S': 2}).astype(int)
        return self

