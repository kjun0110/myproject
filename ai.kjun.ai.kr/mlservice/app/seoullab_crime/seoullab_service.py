import sys
import pandas as pd
import numpy as np
import logging
from seoullab_crime.seoullab_method import SeoullabMethod
from seoullab_crime.kakao_map_singleton import KakaoMapSingleton

logger = logging.getLogger(__name__)

class SeoullabService:

    def __init__(self):
        self.method = SeoullabMethod()

    def preprocess(self):
        logger.info("🦝🦝전처리 시작")
        
        try:
            # 각 파일을 읽어서 데이터프레임으로 변환
            logger.info("CCTV 파일 읽기 시작...")
            cctv = self.method.csv_to_df('cctv.csv')
            cctv = cctv.drop(columns=['2013년도 이전', '2014년', '2015년', '2016년'])
            logger.info(f"CCTV 파일 읽기 완료: {cctv.shape}")
            
            logger.info("Crime 파일 읽기 시작...")
            crime = self.method.csv_to_df('crime.csv')
            #관서명에 따른 경찰서 주소찾기
            station_names = []  # 경찰서 관서명 리스트
            
            for name in crime['관서명']:
                station_names.append('서울' + str(name[:-1]) + '경찰서')
            
            logger.info(f"🔥💧경찰서 관서명 리스트: {station_names}")
            
            station_addrs = []
            station_lats = []
            station_lngs = []
            
            kmaps1 = KakaoMapSingleton()
            kmaps2 = KakaoMapSingleton()
            
            if kmaps1 is kmaps2:
                logger.info("동일한 객체 입니다.")
            else:
                logger.info("다른 객체 입니다.")
            
            kmaps = KakaoMapSingleton()  # 카카오맵 객체 생성
            
            for name in station_names:
                tmp = kmaps.geocode(name, language='ko')
                if tmp and len(tmp) > 0:
                    formatted_addr = tmp[0].get('formatted_address')
                    tmp_loc = tmp[0].get("geometry")
                    lat = tmp_loc['location']['lat']
                    lng = tmp_loc['location']['lng']
                    logger.info(f"{name}의 검색 결과: {formatted_addr} (위도: {lat}, 경도: {lng})")
                    station_addrs.append(formatted_addr)
                    station_lats.append(lat)
                    station_lngs.append(lng)
                else:
                    logger.warning(f"{name}의 검색 결과를 찾을 수 없습니다.")
                    station_addrs.append("")
                    station_lats.append(0.0)
                    station_lngs.append(0.0)
            
            logger.info(f"🔥💧자치구 리스트: {station_addrs}")
            
            gu_names = []
            for addr in station_addrs:
                if addr:  # 주소가 있는 경우만 처리
                    tmp = addr.split()
                    tmp_gu = [gu for gu in tmp if gu[-1] == '구']
                    if tmp_gu:
                        gu_names.append(tmp_gu[0])
                    else:
                        logger.warning(f"주소에서 '구'를 찾을 수 없습니다: {addr}")
                        gu_names.append("")
                else:
                    gu_names.append("")
            
            logger.info(f"🔥💧자치구 리스트 2: {gu_names}")
            
            # 관서명 컬럼을 '서울~~경찰서' 형식으로 변경
            crime['관서명'] = station_names
            
            # 자치구 컬럼을 제일 앞열에 추가
            crime.insert(0, '자치구', gu_names)
            
            logger.info(f"Crime 파일 읽기 완료: {crime.shape}")
            
            # save 폴더에 저장
            from pathlib import Path
            save_path = Path(self.method.dataset.sname)
            save_path.mkdir(exist_ok=True)
            crime_file_path = save_path / 'crime_with_gu.csv'
            crime.to_csv(crime_file_path, index=False, encoding='utf-8-sig')
            logger.info(f"Crime 데이터 저장 완료: {crime_file_path}")
            
            logger.info("Pop 파일 읽기 시작...")
            pop = self.method.xlsx_to_df('pop.xls')
            #POP 칼럼 편집
            # axis = 1방향으로 자치구 열과 4번째 컬럼만 남기고 모두 삭제
            # 자치구는 인덱스 1, 4번째 컬럼은 인덱스 3 ('인구')
            if '자치구' in pop.columns and len(pop.columns) > 3:
                columns_to_keep = ['자치구', pop.columns[3]]  # 자치구와 4번째 컬럼(인구)
                pop = pop[columns_to_keep]
            # axis = 0 방향으로 2,3,4 행 삭제 (인덱스 1,2,3)
            if len(pop) > 3:
                pop = pop.drop(index=[1, 2, 3]).reset_index(drop=True)
            logger.info(f"Pop 파일 읽기 완료: {pop.shape}")
        except FileNotFoundError as e:
            logger.error(f"파일을 찾을 수 없습니다: {e}")
            raise
        except Exception as e:
            logger.error(f"파일 읽기 중 오류 발생: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        # crime_with_gu.csv 파일 읽기 및 편집
        logger.info("crime_with_gu.csv 파일 읽기 시작...")
        # 저장할 때 사용한 경로와 동일한 경로 사용
        from pathlib import Path
        save_path = Path(self.method.dataset.sname)
        crime_file_path = save_path / 'crime_with_gu.csv'
        if not crime_file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {crime_file_path}")
        crime_with_gu = pd.read_csv(crime_file_path)
        
        # crime_with_gu 편집
        # 1번째 컬럼 자치구의 값이 중복되는 경우 중복되는 행들을 합친다.
        # 1번째 컬럼인 자치구의 경우 중복되면 하나의 값만 사용한다.
        # 2번째 컬럼인 관서명의 경우 자치구 컬럼의 값이 중복되면 ','를 사용하여 합친다.
        # 그외 나머지 컬럼인 ~~발생, ~~검거 컬럼의 경우 자치구 컬럼의 값이 중복되는 경우 해당 행의 숫자를 더하여 나타낸다.
        
        # 컬럼 목록 가져오기
        columns = crime_with_gu.columns.tolist()
        자치구_col = columns[0]  # 1번째 컬럼: 자치구
        관서명_col = columns[1]  # 2번째 컬럼: 관서명
        나머지_cols = columns[2:]  # 나머지 컬럼들 (~~발생, ~~검거)
        
        # 숫자 컬럼들을 숫자형으로 변환 (쉼표 제거 후 변환)
        for col in 나머지_cols:
            if crime_with_gu[col].dtype == 'object':
                # 문자열인 경우 쉼표 제거 후 숫자로 변환
                crime_with_gu[col] = crime_with_gu[col].astype(str).str.replace(',', '')
                crime_with_gu[col] = pd.to_numeric(crime_with_gu[col], errors='coerce').fillna(0)
        
        # 자치구별로 그룹화하여 집계
        agg_dict = {
            자치구_col: 'first',  # 자치구: 첫 번째 값만 사용
            관서명_col: lambda x: ','.join(x.astype(str)),  # 관서명: 쉼표로 합치기
        }
        
        # 나머지 컬럼들은 합계
        for col in 나머지_cols:
            agg_dict[col] = 'sum'
        
        # 그룹화 및 집계 수행
        crime_with_gu = crime_with_gu.groupby(자치구_col, as_index=False).agg(agg_dict)
        
        logger.info(f"crime_with_gu.csv 파일 읽기 및 편집 완료: {crime_with_gu.shape}")

        
        # 데이터셋 객체에 저장
        self.method.dataset.cctv = cctv
        self.method.dataset.crime = crime
        self.method.dataset.pop = pop
        self.method.dataset.crime_with_gu = crime_with_gu
        
        logger.info(f"CCTV 데이터: {cctv.shape}")
        logger.info(f"Crime 데이터: {crime.shape}")
        logger.info(f"Pop 데이터: {pop.shape}")
        logger.info(f"crime_with_gu 데이터: {crime_with_gu.shape}")
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
        
        # cctv와 pop 데이터 머지 전략
        # - cctv의 "기관명"과 pop의 "자치구"를 키로 사용
        # - 중복된 컬럼은 자동으로 제거됨
        # - 머지 후 "자치구" 컬럼만 유지하고 "기관명"은 제거
        logger.info("CCTV와 Pop 데이터 머지 시작...")
        cctv_pop = self.method.df_merge(
            right=cctv,  # 기준 데이터프레임
            left=pop,    # 병합할 데이터프레임
            left_on='자치구',  # pop의 키 컬럼
            right_on='기관명',  # cctv의 키 컬럼
            how='left',  # left join (cctv 기준)
            keep_key='left'  # "자치구" 컬럼만 유지
        )
        logger.info(f"CCTV-Pop 머지 완료: {cctv_pop.shape}")
        
        # 머지된 데이터를 데이터셋 객체에 저장
        self.method.dataset.cctv = cctv
        self.method.dataset.crime = crime
        self.method.dataset.pop = pop

        return {
            "message": "전처리 완료",
            "cctv": df_to_dict(cctv),
            "crime": df_to_dict(crime),
            "pop": df_to_dict(pop),
            "cctv_pop": df_to_dict(cctv_pop)
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
            data_type: 'cctv', 'crime', 'pop', 'crime_with_gu' 중 하나
        
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
            return df_to_dict(df)
        elif data_type.lower() == 'pop':
            df = self.method.dataset.pop
            if df is None:
                raise ValueError(f"{data_type} 데이터가 로드되지 않았습니다.")
            return df_to_dict(df)
        elif data_type.lower() == 'crime_with_gu':
            df = self.method.dataset.crime_with_gu
            if df is None:
                raise ValueError(f"{data_type} 데이터가 로드되지 않았습니다.")
            return df_to_dict(df)
        else:
            raise ValueError(f"지원하지 않는 데이터 타입입니다: {data_type}. 'cctv', 'crime', 'pop', 'crime_with_gu' 중 하나를 선택하세요.")