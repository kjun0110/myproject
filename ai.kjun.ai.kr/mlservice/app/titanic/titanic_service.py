import pandas as pd
import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from titanic.titanic_method import TitanicMethod
from titanic.titanic_dataset import TitanicDataSet

logger = logging.getLogger(__name__)

# LightGBM import (에러 발생 시 기본값 사용)
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except (ImportError, OSError) as e:
    logger.error(f"LightGBM import 실패: {e}")
    logger.error("LightGBM이 설치되지 않았거나 필요한 시스템 라이브러리가 없습니다.")
    logger.error("Dockerfile에 'RUN apt-get update && apt-get install -y libgomp1' 추가 필요")
    LIGHTGBM_AVAILABLE = False
    # 더미 객체 생성 (에러 방지)
    class DummyLGBM:
        def __init__(self, *args, **kwargs):
            pass
    lgb = type('lgb', (), {'LGBMClassifier': DummyLGBM})()


class PassengerService:
    """Titanic Passenger CRUD 서비스"""
    
    def __init__(self):
        # CSV 파일 경로 설정
        current_file = Path(__file__).resolve()
        # app/titanic/titanic_service.py -> app/titanic/ (같은 디렉토리)
        titanic_dir = current_file.parent
        self.train_csv_path = titanic_dir / "train.csv"
        self.test_csv_path = titanic_dir / "test.csv"
        # 전처리된 데이터와 모델 저장
        self.processed_data = None
        self.models = {}
        self.y_train = None
    
    def _get_csv_path(self, filename: str) -> Path:
        """
        CSV 파일의 전체 경로를 반환
        
        Args:
            filename: CSV 파일명 (train.csv 또는 test.csv)
        
        Returns:
            CSV 파일의 Path 객체
        """
        if filename == "train.csv":
            return self.train_csv_path
        elif filename == "test.csv":
            return self.test_csv_path
        else:
            # 기본적으로 titanic 폴더에서 찾기
            current_file = Path(__file__).resolve()
            titanic_dir = current_file.parent
            return titanic_dir / filename

    def preprocess(self) -> Dict[str, Any]:
        logger.info("🦝🦝전처리 시작")
        the_method = TitanicMethod()

        #train
        train_csv_path = self._get_csv_path('train.csv')
        df_train = the_method.read_csv(str(train_csv_path))
        # Survived label 저장
        self.y_train = df_train['Survived']
        this_train = the_method.create_df(df_train, 'Survived')
        logger.info(f"Train CSV 파일 경로: {train_csv_path}")
        logger.info(f'1. Train 의 type \n {type(this_train)} ')
        logger.info(f'2. Train 의 column \n {this_train.columns} ')
        logger.info(f'3. Train 의 상위 5개 행\n {this_train.head(5)} ')
        logger.info(f'4. Train 의 null 의 갯수\n {this_train.isnull().sum().sum()}개')

        #test
        test_csv_path = self._get_csv_path('test.csv')
        df_test = the_method.read_csv(str(test_csv_path))
        this_test = the_method.create_df(df_test, 'Survived')
        logger.info(f"Test CSV 파일 경로: {test_csv_path}")
        logger.info(f'1. Test 의 type \n {type(this_test)} ')
        logger.info(f'2. Test 의 column \n {this_test.columns} ')
        logger.info(f'3. Test 의 상위 5개 행\n {this_test.head(5)} ')
        logger.info(f'4. Test 의 null 의 갯수\n {this_test.isnull().sum().sum()}개')
        
        this = TitanicDataSet()

        this.train = this_train
        this.test = this_test

        drop_features = ['SibSp', 'Parch', 'Cabin', 'Ticket']
        this = the_method.drop_feature(this, *drop_features)
        this = the_method.pclass_ordinal(this)
        this = the_method.title_nominal(this)
        this = the_method.gender_nominal(this)
        this = the_method.age_ratio(this)
        this = the_method.fare_ordinal(this)
        this = the_method.embarked_ordinal(this)
        drop_name = ['Name']
        this = the_method.drop_feature(this, *drop_name)

        # 전처리 후 null 확인
        the_method.check_null(this)
        
        logger.info("🦝🦝 train 전처리 완료")
        logger.info(f'1. Train 의 type \n {type(this.train)} ')
        logger.info(f'2. Train 의 column \n {this.train.columns} ')
        logger.info(f'3. Train 의 상위 5개 행\n {this.train.head(5)} ')
        logger.info(f'4. Train 의 null 의 갯수\n {this.train.isnull().sum().sum()}개')

        logger.info("🦝🦝 test 전처리 완료")
        logger.info(f'1. Test 의 type \n {type(this.test)}')
        logger.info(f'2. Test 의 column \n {this.test.columns}')
        logger.info(f'3. Test 의 상위 5개 행\n {this.test.head(5)}')
        logger.info(f'4. Test 의 null 의 갯수\n {this.test.isnull().sum().sum()}개')

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
        
        # 전처리된 데이터 저장
        self.processed_data = this
        
        return {
            "message": "전처리 완료",
            "train": df_to_dict(this.train),
            "test": df_to_dict(this.test)
        }

    def modeling(self):
        logger.info("🦝🦝모델링 시작")

        if self.processed_data is None:
            logger.warning("전처리된 데이터가 없습니다. 먼저 preprocess()를 실행하세요.")
            return
        
        # 모델 초기화
        self.models = {
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'naive_bayes': GaussianNB(),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'svm': SVC(random_state=42, probability=True)
        }
        
        # LightGBM 추가 (사용 가능한 경우)
        if LIGHTGBM_AVAILABLE:
            self.models['lightgbm'] = lgb.LGBMClassifier(random_state=42, verbose=-1)
        else:
            # LightGBM이 없어도 결과에 포함되도록 더미 모델 추가
            logger.warning("LightGBM이 없습니다. 더미 모델을 사용합니다.")
            class DummyLightGBMModel:
                def fit(self, X, y):
                    logger.warning("LightGBM 더미 모델: fit 호출됨")
                    return self
                def predict(self, X):
                    logger.warning("LightGBM 더미 모델: predict 호출됨")
                    return [0] * len(X)
            self.models['lightgbm'] = DummyLightGBMModel()
        
        logger.info(f"🦝🦝모델링 완료 - 총 {len(self.models)}개 모델: {list(self.models.keys())}")

    def learning(self):
        logger.info("🦝🦝학습 시작")

        if self.processed_data is None or not self.models:
            logger.warning("전처리된 데이터나 모델이 없습니다. 먼저 preprocess()와 modeling()을 실행하세요.")
            return
        
        if self.y_train is None:
            logger.warning("학습용 label이 없습니다. 먼저 preprocess()를 실행하세요.")
            return
        
        X_train = self.processed_data.train.copy()
        y_train = self.y_train
        
        # PassengerId가 있으면 제거 (ID는 학습에 사용하지 않음)
        if 'PassengerId' in X_train.columns:
            X_train = X_train.drop(columns=['PassengerId'])
            logger.info("PassengerId 컬럼을 제거했습니다.")
        
        # 모든 컬럼을 숫자형으로 변환 (object 타입 제거)
        for col in X_train.columns:
            if X_train[col].dtype == 'object':
                logger.warning(f"{col} 컬럼이 object 타입입니다. 숫자형으로 변환합니다.")
                X_train[col] = pd.to_numeric(X_train[col], errors='coerce').fillna(0).astype(int)
        
        logger.info(f"학습 데이터 타입: {X_train.dtypes}")
        
        # 각 모델 학습
        for model_name, model in self.models.items():
            logger.info(f"{model_name} 학습 중...")
            try:
                model.fit(X_train, y_train)
                logger.info(f"{model_name} 학습 완료")
            except Exception as e:
                logger.error(f"{model_name} 학습 중 오류 발생: {e}")
                raise
        
        logger.info("🦝🦝학습 완료")

    def evaluate(self) -> Dict[str, Any]:
        logger.info("🦝🦝평가 시작")

        if self.processed_data is None or not self.models:
            logger.warning("전처리된 데이터나 모델이 없습니다. 먼저 preprocess(), modeling(), learning()을 실행하세요.")
            return {"error": "모델이 학습되지 않았습니다."}
        
        if self.y_train is None:
            logger.warning("학습용 label이 없습니다.")
            return {"error": "학습용 label이 없습니다."}
        
        X_train = self.processed_data.train.copy()
        y_train = self.y_train
        
        # PassengerId가 있으면 제거 (ID는 학습에 사용하지 않음)
        if 'PassengerId' in X_train.columns:
            X_train = X_train.drop(columns=['PassengerId'])
            logger.info("PassengerId 컬럼을 제거했습니다.")
        
        # 모든 컬럼을 숫자형으로 변환 (object 타입 제거)
        for col in X_train.columns:
            if X_train[col].dtype == 'object':
                logger.warning(f"{col} 컬럼이 object 타입입니다. 숫자형으로 변환합니다.")
                X_train[col] = pd.to_numeric(X_train[col], errors='coerce').fillna(0).astype(int)
        
        logger.info(f"평가 데이터 타입: {X_train.dtypes}")
        
        # Train 데이터를 train/validation으로 분할
        X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        
        # 각 모델 재학습 및 평가
        logger.info(f"평가할 모델 목록: {list(self.models.keys())}")
        results = {}
        for model_name, model in self.models.items():
            logger.info(f"{model_name} 재학습 및 평가 중...")
            try:
                # Validation set으로 재학습
                model.fit(X_train_split, y_train_split)
                # Validation set으로 예측
                y_pred = model.predict(X_val_split)
                accuracy = accuracy_score(y_val_split, y_pred)
                results[model_name] = float(accuracy)
                logger.info(f'{model_name} 활용한 검증 정확도 {accuracy:.4f}')
            except Exception as e:
                logger.error(f"{model_name} 평가 중 오류 발생: {e}")
                import traceback
                logger.error(traceback.format_exc())
                results[model_name] = None
        
        logger.info("🦝🦝평가 완료")
        
        return {
            "message": "평가 완료",
            "results": results
        }

    def postprocess(self):
        logger.info("🦝🦝후처리 시작")
        logger.info("🦝🦝후처리 완료")


    def submit(self, model_name: str = None) -> Dict[str, Any]:
        """
        Kaggle 제출 파일 생성
        model_name이 None이면 정확도가 가장 높은 모델을 자동으로 선택합니다.
        
        Args:
            model_name: 사용할 모델 이름 (None이면 자동 선택)
                        'logistic_regression', 'naive_bayes', 'random_forest', 'lightgbm', 'svm'
        
        Returns:
            제출 파일 경로와 정보
        """
        logger.info("🦝🦝제출 시작")
        
        if self.processed_data is None or not self.models:
            logger.warning("전처리된 데이터나 모델이 없습니다. 먼저 preprocess(), modeling(), learning()을 실행하세요.")
            return {"error": "모델이 학습되지 않았습니다."}
        
        # model_name이 None이면 정확도가 가장 높은 모델 자동 선택
        if model_name is None:
            logger.info("모델이 지정되지 않았습니다. 정확도가 가장 높은 모델을 자동으로 선택합니다.")
            
            # 먼저 평가를 실행하여 각 모델의 정확도 확인
            evaluation_result = self.evaluate()
            
            if "error" in evaluation_result:
                logger.warning("평가 실패. 기본 모델(random_forest)을 사용합니다.")
                model_name = 'random_forest'
            else:
                results = evaluation_result.get("results", {})
                if not results:
                    logger.warning("평가 결과가 없습니다. 기본 모델(random_forest)을 사용합니다.")
                    model_name = 'random_forest'
                else:
                    # None이 아닌 결과 중에서 정확도가 가장 높은 모델 선택
                    valid_results = {k: v for k, v in results.items() if v is not None}
                    if not valid_results:
                        logger.warning("유효한 평가 결과가 없습니다. 기본 모델(random_forest)을 사용합니다.")
                        model_name = 'random_forest'
                    else:
                        best_model = max(valid_results.items(), key=lambda x: x[1])
                        model_name = best_model[0]
                        logger.info(f"정확도가 가장 높은 모델 선택: {model_name} (정확도: {best_model[1]:.4f})")
        
        if model_name not in self.models:
            logger.error(f"모델 '{model_name}'이 없습니다. 사용 가능한 모델: {list(self.models.keys())}")
            return {"error": f"모델 '{model_name}'이 없습니다."}
        
        # Test 데이터 준비
        X_test = self.processed_data.test.copy()
        
        # PassengerId 저장
        if 'PassengerId' not in X_test.columns:
            logger.error("PassengerId 컬럼이 없습니다.")
            return {"error": "PassengerId 컬럼이 없습니다."}
        
        passenger_ids = X_test['PassengerId'].copy()
        X_test = X_test.drop(columns=['PassengerId'])
        
        # 모든 컬럼을 숫자형으로 변환 (object 타입 제거)
        for col in X_test.columns:
            if X_test[col].dtype == 'object':
                logger.warning(f"{col} 컬럼이 object 타입입니다. 숫자형으로 변환합니다.")
                X_test[col] = pd.to_numeric(X_test[col], errors='coerce').fillna(0).astype(int)
        
        # Train 데이터로 모델 재학습
        X_train = self.processed_data.train.copy()
        y_train = self.y_train
        
        # PassengerId 제거
        if 'PassengerId' in X_train.columns:
            X_train = X_train.drop(columns=['PassengerId'])
        
        # 모든 컬럼을 숫자형으로 변환
        for col in X_train.columns:
            if X_train[col].dtype == 'object':
                X_train[col] = pd.to_numeric(X_train[col], errors='coerce').fillna(0).astype(int)
        
        # 모델 선택 및 학습
        model = self.models[model_name]
        logger.info(f"{model_name} 모델로 전체 학습 데이터로 재학습 중...")
        model.fit(X_train, y_train)
        logger.info(f"{model_name} 모델 학습 완료")
        
        # 예측
        logger.info(f"{model_name} 모델로 예측 중...")
        predictions = model.predict(X_test)
        logger.info(f"예측 완료: {len(predictions)}개")
        
        # 제출 파일 생성
        submission_df = pd.DataFrame({
            'PassengerId': passenger_ids,
            'Survived': predictions.astype(int)
        })
        
        # kaggle 폴더에 저장
        current_file = Path(__file__).resolve()
        kaggle_dir = current_file.parent.parent / "kaggle"
        kaggle_dir.mkdir(exist_ok=True)
        
        # 파일명: submission_{model_name}_{timestamp}.csv
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"submission_{model_name}_{timestamp}.csv"
        filepath = kaggle_dir / filename
        
        submission_df.to_csv(filepath, index=False)
        logger.info(f"제출 파일 생성 완료: {filepath}")
        logger.info(f"파일 크기: {len(submission_df)}행")
        logger.info(f"생존 예측 수: {int(predictions.sum())}명")
        
        logger.info("🦝🦝제출 완료")
        
        # 평가 결과에서 선택된 모델의 정확도 가져오기
        evaluation_result = self.evaluate()
        model_accuracy = None
        if "results" in evaluation_result:
            model_accuracy = evaluation_result["results"].get(model_name)
        
        result = {
            "message": "제출 파일 생성 완료",
            "model": model_name,
            "filepath": str(filepath),
            "filename": filename,
            "total_passengers": int(len(submission_df)),
            "predicted_survived": int(predictions.sum()),
            "predicted_not_survived": int(len(predictions) - predictions.sum())
        }
        
        if model_accuracy is not None:
            result["model_accuracy"] = float(model_accuracy)
            result["auto_selected"] = (model_name is None or model_name == "auto")
        
        return result