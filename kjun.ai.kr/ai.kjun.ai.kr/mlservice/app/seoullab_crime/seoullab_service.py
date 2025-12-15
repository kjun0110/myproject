import sys
import pandas as pd
import numpy as np
import logging
import json
import folium
from pathlib import Path
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
            
            logger.info("Pop 파일 읽기 시작...")
            # Excel 파일을 읽을 때 첫 번째 행을 컬럼명으로 사용 (header=0)
            pop_filepath = self.method.data_path / 'pop.xls'
            file_ext = pop_filepath.suffix.lower()
            engine = 'xlrd' if file_ext == '.xls' else 'openpyxl'
            pop = pd.read_excel(pop_filepath, engine=engine, header=0)
            
            #POP 칼럼 편집
            # axis = 1방향으로 자치구 열과 4번째 컬럼만 남기고 모두 삭제
            # 자치구는 인덱스 1, 4번째 컬럼은 인덱스 3 ('인구')
            if '자치구' in pop.columns and len(pop.columns) > 3:
                columns_to_keep = ['자치구', pop.columns[3]]  # 자치구와 4번째 컬럼(인구)
                pop = pop[columns_to_keep]
            
            # 첫 번째 행(컬럼명) 아래부터 3개 행(인덱스 0, 1, 2) 삭제
            # 이 행들은 자치구 관련 헤더 정보이므로 삭제
            # 삭제 후 종로구부터 데이터가 시작됨
            if len(pop) > 3:
                pop = pop.drop(index=[0, 1, 2]).reset_index(drop=True)
                logger.info("컬럼명 아래 3개 행(인덱스 0, 1, 2) 삭제 완료")
            
            # "합계" 행 제거 (데이터가 아닌 합계 행)
            if len(pop) > 0:
                pop = pop[pop['자치구'] != '합계'].reset_index(drop=True)
                logger.info("합계 행 제거 완료")
            
            # null 값이 있는 행 제거
            pop = pop.dropna(subset=['자치구', '인구']).reset_index(drop=True)
            
            logger.info(f"Pop 파일 읽기 완료: {pop.shape}")
            logger.info(f"Pop 자치구 목록: {pop['자치구'].tolist()}")
        except FileNotFoundError as e:
            logger.error(f"파일을 찾을 수 없습니다: {e}")
            raise
        except Exception as e:
            logger.error(f"파일 읽기 중 오류 발생: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        # crime_with_gu 데이터 생성 및 편집 (메모리에서 직접 처리)
        logger.info("crime_with_gu 데이터 생성 및 편집 시작...")
        # crime 데이터프레임을 crime_with_gu로 복사
        crime_with_gu = crime.copy()
        
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
        
        # crime_with_gu와 pop 데이터 머지 전략
        # - crime_with_gu의 "자치구"와 pop의 "자치구"를 키로 사용
        # - left join (crime_with_gu 기준)
        # - 머지 후 "자치구" 컬럼만 유지하고 "관서명"은 제거
        logger.info("Crime_with_gu와 Pop 데이터 머지 시작...")
        
        # "관서명" 컬럼을 제거한 crime_with_gu 복사본 생성 (자치구는 유지)
        crime_with_gu_for_merge = crime_with_gu.drop(columns=['관서명']) if '관서명' in crime_with_gu.columns else crime_with_gu.copy()
        
        # 자치구 컬럼 값 정규화 (공백 제거, 앞뒤 공백 제거)
        crime_with_gu_for_merge = crime_with_gu_for_merge.copy()
        pop_for_merge = pop.copy()
        
        if '자치구' in crime_with_gu_for_merge.columns:
            crime_with_gu_for_merge['자치구'] = crime_with_gu_for_merge['자치구'].astype(str).str.strip().str.replace(' ', '').str.replace('\t', '').str.replace('\n', '')
        
        if '자치구' in pop_for_merge.columns:
            pop_for_merge['자치구'] = pop_for_merge['자치구'].astype(str).str.strip().str.replace(' ', '').str.replace('\t', '').str.replace('\n', '')
        
        # 머지 전 자치구 값 확인 (디버깅용)
        logger.info(f"Crime_with_gu 자치구 값 샘플: {crime_with_gu_for_merge['자치구'].head(5).tolist()}")
        logger.info(f"Pop 자치구 값 샘플: {pop_for_merge['자치구'].head(5).tolist()}")
        
        # pop의 "자치구"와 crime_with_gu의 "자치구"로 머지
        crime_pop = pd.merge(
            crime_with_gu_for_merge,  # left (기준 데이터프레임)
            pop_for_merge,  # right (병합할 데이터프레임)
            left_on='자치구',
            right_on='자치구',
            how='left',
            suffixes=('', '_pop')
        )
        
        # 머지 결과 확인 (인구가 null인 행 확인)
        null_pop_count = crime_pop['인구'].isnull().sum()
        if null_pop_count > 0:
            null_pop_gu = crime_pop[crime_pop['인구'].isnull()]['자치구'].tolist()
            logger.warning(f"인구가 null인 자치구: {null_pop_gu}")
            logger.warning(f"Pop 데이터의 자치구 목록: {pop_for_merge['자치구'].tolist()}")
            logger.warning(f"Crime_with_gu 데이터의 자치구 목록: {crime_with_gu_for_merge['자치구'].tolist()}")
        
        # pop에서 가져온 "자치구" 컬럼이 있다면 제거 (이미 crime_with_gu에 있음)
        if '자치구_pop' in crime_pop.columns:
            crime_pop = crime_pop.drop(columns=['자치구_pop'])
        
        # "자치구" 컬럼이 첫 번째 컬럼이 되도록 컬럼 순서 조정
        if '자치구' in crime_pop.columns:
            cols = ['자치구'] + [col for col in crime_pop.columns if col != '자치구']
            crime_pop = crime_pop[cols]
        
        logger.info(f"Crime-Pop 머지 완료: {crime_pop.shape}")
        logger.info(f"Crime-Pop 컬럼: {crime_pop.columns.tolist()}")
        
        # CCTV와 crime_pop 데이터 머지 (자치구 기준, 소계 컬럼만)
        logger.info("CCTV와 Crime-Pop 데이터 머지 시작...")
        
        # CCTV 데이터에서 기관명과 소계만 추출
        cctv_for_merge = cctv[['기관명', '소계']].copy()
        
        # 자치구 컬럼 값 정규화
        cctv_for_merge['기관명'] = cctv_for_merge['기관명'].astype(str).str.strip().str.replace(' ', '').str.replace('\t', '').str.replace('\n', '')
        crime_pop_for_merge = crime_pop.copy()
        if '자치구' in crime_pop_for_merge.columns:
            crime_pop_for_merge['자치구'] = crime_pop_for_merge['자치구'].astype(str).str.strip().str.replace(' ', '').str.replace('\t', '').str.replace('\n', '')
        
        # CCTV 소계를 숫자형으로 변환
        if cctv_for_merge['소계'].dtype == 'object':
            cctv_for_merge['소계'] = cctv_for_merge['소계'].astype(str).str.replace(',', '').str.replace(' ', '')
        cctv_for_merge['소계'] = pd.to_numeric(cctv_for_merge['소계'], errors='coerce').fillna(0)
        
        # crime_pop과 CCTV 머지 (자치구 = 기관명)
        cctv_crime_pop = pd.merge(
            crime_pop_for_merge,  # left (기준 데이터프레임)
            cctv_for_merge,  # right (병합할 데이터프레임)
            left_on='자치구',
            right_on='기관명',
            how='left',
            suffixes=('', '_cctv')
        )
        
        # 기관명 컬럼 제거 (자치구만 유지)
        if '기관명' in cctv_crime_pop.columns:
            cctv_crime_pop = cctv_crime_pop.drop(columns=['기관명'])
        
        # 소계 컬럼명을 CCTV로 변경 (명확성을 위해)
        if '소계' in cctv_crime_pop.columns:
            cctv_crime_pop = cctv_crime_pop.rename(columns={'소계': 'CCTV'})
        
        # CCTV가 null인 경우 0으로 채우기
        if 'CCTV' in cctv_crime_pop.columns:
            cctv_crime_pop['CCTV'] = cctv_crime_pop['CCTV'].fillna(0)
        
        logger.info(f"CCTV-Crime-Pop 머지 완료: {cctv_crime_pop.shape}")
        logger.info(f"CCTV-Crime-Pop 컬럼: {cctv_crime_pop.columns.tolist()}")
        
        # cctv_crime_pop 데이터 가공: 발생/검거 컬럼 합치기
        # 자치구 컬럼 찾기
        자치구_col = None
        for col in ['자치구', '기관명']:
            if col in cctv_crime_pop.columns:
                자치구_col = col
                break
        
        if 자치구_col is None:
            raise ValueError("자치구 컬럼을 찾을 수 없습니다.")
        
        # 발생 컬럼 추출 및 합계 계산
        발생_cols = [col for col in cctv_crime_pop.columns if '발생' in col]
        범죄발생 = pd.Series(0, index=cctv_crime_pop.index)
        for col in 발생_cols:
            발생_값 = cctv_crime_pop[col].copy()
            # 숫자형으로 변환
            if 발생_값.dtype == 'object':
                발생_값 = 발생_값.astype(str).str.replace(',', '').str.replace(' ', '')
            발생_값 = pd.to_numeric(발생_값, errors='coerce').fillna(0)
            범죄발생 += 발생_값
        
        # 검거 컬럼 추출 및 합계 계산
        검거_cols = [col for col in cctv_crime_pop.columns if '검거' in col]
        범죄검거 = pd.Series(0, index=cctv_crime_pop.index)
        for col in 검거_cols:
            검거_값 = cctv_crime_pop[col].copy()
            # 숫자형으로 변환
            if 검거_값.dtype == 'object':
                검거_값 = 검거_값.astype(str).str.replace(',', '').str.replace(' ', '')
            검거_값 = pd.to_numeric(검거_값, errors='coerce').fillna(0)
            범죄검거 += 검거_값
        
        # 인구 컬럼 찾기
        인구_col = None
        for col in ['인구', '인구수', '총인구']:
            if col in cctv_crime_pop.columns:
                인구_col = col
                break
        
        if 인구_col is None:
            raise ValueError("인구 컬럼을 찾을 수 없습니다.")
        
        # 인구 데이터 가져오기 및 숫자형 변환
        인구_값 = cctv_crime_pop[인구_col].copy()
        if 인구_값.dtype == 'object':
            인구_값 = 인구_값.astype(str).str.replace(',', '').str.replace(' ', '')
        인구_값 = pd.to_numeric(인구_값, errors='coerce').fillna(0)
        
        # CCTV 데이터 가져오기
        cctv_값 = cctv_crime_pop['CCTV'].copy()
        if cctv_값.dtype == 'object':
            cctv_값 = cctv_값.astype(str).str.replace(',', '').str.replace(' ', '')
        cctv_값 = pd.to_numeric(cctv_값, errors='coerce').fillna(0)
        
        # 최종 데이터프레임 생성 (자치구, 범죄발생, 범죄검거, 인구, CCTV만)
        cctv_crime_pop = pd.DataFrame({
            '자치구': cctv_crime_pop[자치구_col],
            '범죄발생': 범죄발생.values,
            '범죄검거': 범죄검거.values,
            '인구': 인구_값.values,
            'CCTV': cctv_값.values
        })
        
        logger.info(f"CCTV-Crime-Pop 데이터 가공 완료: {cctv_crime_pop.shape}")
        logger.info(f"CCTV-Crime-Pop 최종 컬럼: {cctv_crime_pop.columns.tolist()}")
        
        # 머지된 데이터를 데이터셋 객체에 저장
        self.method.dataset.cctv = cctv
        self.method.dataset.crime = crime
        self.method.dataset.pop = pop
        self.method.dataset.crime_with_gu = crime_with_gu
        self.method.dataset.crime_pop = crime_pop
        self.method.dataset.cctv_crime_pop = cctv_crime_pop

        return {
            "message": "전처리 완료",
            "cctv": df_to_dict(cctv),
            "crime": df_to_dict(crime),
            "pop": df_to_dict(pop),
            "cctv_pop": df_to_dict(cctv_pop),
            "crime_pop": df_to_dict(crime_pop),
            "cctv_crime_pop": df_to_dict(cctv_crime_pop)
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

    def save_csv(self):
        """
        crime_with_gu.csv 파일 저장
        
        Returns:
            dict: 저장 결과
        """
        logger.info("🦝🦝CSV 저장 시작")
        
        # 전처리가 실행되지 않았다면 실행
        if self.method.dataset.crime_with_gu is None:
            logger.info("전처리가 실행되지 않았습니다. 전처리를 실행합니다.")
            self.preprocess()
        
        # crime_with_gu 데이터 가져오기
        crime_with_gu = self.method.dataset.crime_with_gu
        if crime_with_gu is None:
            raise ValueError("crime_with_gu 데이터가 없습니다. 전처리를 먼저 실행해주세요.")
        
        # save_path 확인 및 생성
        from pathlib import Path
        current_file = Path(__file__)
        save_path = current_file.parent / "save"
        save_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"저장 경로: {save_path}")
        logger.info(f"저장 경로 절대 경로: {save_path.resolve()}")
        
        # crime_with_gu.csv 저장
        logger.info("crime_with_gu.csv 저장 시작...")
        crime_file_path = save_path / 'crime_with_gu.csv'
        crime_with_gu.to_csv(crime_file_path, index=False, encoding='utf-8-sig')
        logger.info(f"crime_with_gu.csv 저장 완료: {crime_file_path}")
        
        logger.info("🦝🦝CSV 저장 완료")
        
        return {
            "message": "crime_with_gu.csv 저장 완료",
            "file_path": str(crime_file_path),
            "file_exists": crime_file_path.exists()
        }

    def submit(self):
        """
        최종 결과물 제출 (crime_with_gu.csv 및 히트맵 생성 및 저장)
        
        Returns:
            dict: 저장 결과
        """
        logger.info("🦝🦝제출 시작 (데이터 및 히트맵 저장)")
        
        # 전처리가 실행되지 않았다면 실행
        if self.method.dataset.crime_pop is None:
            logger.info("전처리가 실행되지 않았습니다. 전처리를 실행합니다.")
            self.preprocess()
        
        # crime_pop 데이터 가져오기 (crime_with_gu + pop 머지된 데이터)
        crime_pop = self.method.dataset.crime_pop
        if crime_pop is None:
            raise ValueError("crime_pop 데이터가 없습니다. 전처리를 먼저 실행해주세요.")
        
        # save_path 확인 및 생성
        from pathlib import Path
        current_file = Path(__file__)
        save_path = current_file.parent / "save"
        save_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"저장 경로: {save_path}")
        logger.info(f"저장 경로 절대 경로: {save_path.resolve()}")
        
        # crime_with_gu.csv 저장 (원본 데이터)
        crime_file_path = None
        if self.method.dataset.crime_with_gu is not None:
            logger.info("crime_with_gu.csv 저장 시작...")
            crime_file_path = save_path / 'crime_with_gu.csv'
            self.method.dataset.crime_with_gu.to_csv(crime_file_path, index=False, encoding='utf-8-sig')
            logger.info(f"crime_with_gu.csv 저장 완료: {crime_file_path}")
        
        # 범죄 발생률 히트맵 생성 (crime_pop 사용, 인구 10만명당 정규화)
        logger.info("범죄 발생률 히트맵 생성 시작 (인구 10만명당 정규화)...")
        try:
            import matplotlib
            matplotlib.use('Agg')  # 백엔드 설정 (GUI 없이 사용, import 전에 설정)
            import matplotlib.pyplot as plt
            import matplotlib.font_manager as fm
            import seaborn as sns
            import platform
            
            # 한글 폰트 설정 (OS별로 다른 폰트 사용)
            plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
            
            # 시스템에 설치된 한글 폰트 찾기
            system = platform.system()
            korean_fonts = []
            
            if system == 'Windows':
                korean_fonts = ['Malgun Gothic', 'NanumGothic', 'Gulim', 'Batang']
            elif system == 'Darwin':  # macOS
                korean_fonts = ['AppleGothic', 'NanumGothic', 'Arial Unicode MS']
            else:  # Linux
                korean_fonts = ['NanumGothic', 'NanumBarunGothic', 'DejaVu Sans', 'Noto Sans CJK KR']
            
            # 폰트 캐시 초기화 (새로 설치된 폰트 인식)
            try:
                fm._rebuild()
            except:
                pass
            
            # 사용 가능한 폰트 찾기
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            font_found = False
            
            for font_name in korean_fonts:
                if font_name in available_fonts:
                    plt.rcParams['font.family'] = font_name
                    logger.info(f"한글 폰트 설정 완료: {font_name}")
                    font_found = True
                    break
            
            # 폰트를 찾지 못한 경우, 폰트 경로 직접 지정 시도
            if not font_found:
                # NanumGothic 폰트 경로 시도 (일반적인 경로)
                nanum_paths = [
                    '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                    '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
                    '/System/Library/Fonts/AppleGothic.ttf',
                    'C:/Windows/Fonts/malgun.ttf',
                    'C:/Windows/Fonts/gulim.ttc'
                ]
                
                for font_path in nanum_paths:
                    try:
                        from pathlib import Path
                        if Path(font_path).exists():
                            font_prop = fm.FontProperties(fname=font_path)
                            plt.rcParams['font.family'] = font_prop.get_name()
                            logger.info(f"한글 폰트 경로로 설정 완료: {font_path}")
                            font_found = True
                            break
                    except:
                        continue
                
                # 여전히 폰트를 찾지 못한 경우 기본 설정
                if not font_found:
                    logger.warning("한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
                    # 한글 대신 영문으로 표시되거나 깨질 수 있음
                    plt.rcParams['font.family'] = 'DejaVu Sans'
            
            # save_path는 이미 위에서 생성됨
            logger.info(f"히트맵 저장 경로: {save_path}")
            
            # 컬럼 목록 가져오기
            columns = crime_pop.columns.tolist()
            자치구_col = columns[0]  # 1번째 컬럼: 자치구
            
            # 발생 컬럼만 추출 (검거 제외)
            발생_cols = [col for col in crime_pop.columns if '발생' in col]
            
            if not 발생_cols:
                raise ValueError("발생 컬럼을 찾을 수 없습니다.")
            
            # 히트맵용 데이터프레임 생성 (crime_pop 사용)
            heatmap_data = crime_pop.set_index(자치구_col)[발생_cols].copy()
            
            # 범죄 유형명 정리 (컬럼명에서 ' 발생' 제거)
            heatmap_data.columns = [col.replace(' 발생', '') for col in heatmap_data.columns]
            
            # 발생 데이터를 숫자형으로 변환 (문자열이나 쉼표 제거 후 변환)
            for col in heatmap_data.columns:
                if heatmap_data[col].dtype == 'object':
                    heatmap_data[col] = heatmap_data[col].astype(str).str.replace(',', '').str.replace(' ', '')
                heatmap_data[col] = pd.to_numeric(heatmap_data[col], errors='coerce').fillna(0)
            
            # 인구 데이터 가져오기 및 숫자형으로 변환
            인구_data = crime_pop.set_index(자치구_col)['인구'].copy()
            
            # 인구 데이터를 숫자형으로 변환 (문자열이나 쉼표 제거 후 변환)
            if 인구_data.dtype == 'object':
                인구_data = 인구_data.astype(str).str.replace(',', '').str.replace(' ', '')
            인구_data = pd.to_numeric(인구_data, errors='coerce')
            
            # null 값이 있는 경우 경고 및 처리
            if 인구_data.isnull().any():
                null_gu = 인구_data[인구_data.isnull()].index.tolist()
                logger.warning(f"인구 데이터가 null인 자치구: {null_gu}")
                # null 값을 1로 설정하여 0으로 나누는 것을 방지 (또는 해당 행 제외)
                인구_data = 인구_data.fillna(1)
            
            # 인구가 0인 경우도 처리
            인구_data = 인구_data.replace(0, 1)
            
            # 인구 100,000명당 범죄건수로 변환
            # 각 범죄건수를 인구로 나누고 100,000을 곱함
            heatmap_data_per_100k = heatmap_data.div(인구_data, axis=0) * 100000
            
            # 무한대나 null 값 처리
            heatmap_data_per_100k = heatmap_data_per_100k.replace([np.inf, -np.inf], np.nan)
            heatmap_data_per_100k = heatmap_data_per_100k.fillna(0)
            
            # 각 범죄 유형(컬럼)별로 최댓값을 찾아서 정규화
            # 각 컬럼의 최댓값을 1로 하여 각각 정규화
            heatmap_data_normalized = heatmap_data_per_100k.copy()
            
            for col in heatmap_data_per_100k.columns:
                col_max = heatmap_data_per_100k[col].max()
                if pd.isna(col_max) or col_max == 0:
                    logger.warning(f"{col}의 최댓값이 0이거나 null입니다. 정규화를 건너뜁니다.")
                    # 최댓값이 0이면 그대로 유지
                else:
                    # 각 컬럼의 최댓값으로 나누어 0~1 사이로 정규화 (가장 큰 값이 1이 되도록)
                    heatmap_data_normalized[col] = heatmap_data_per_100k[col] / col_max
                    logger.info(f"{col} 최댓값: {col_max:.2f} (인구 10만명당), 정규화 완료")
            
            # 최종 데이터 타입 확인 및 변환 (float64로 명시적 변환)
            heatmap_data_normalized = heatmap_data_normalized.astype(float)
            
            # 무한대나 null 값 최종 처리
            heatmap_data_normalized = heatmap_data_normalized.replace([np.inf, -np.inf], np.nan)
            heatmap_data_normalized = heatmap_data_normalized.fillna(0)
            
            # 히트맵 생성
            plt.figure(figsize=(12, 10))
            sns.heatmap(
                heatmap_data_normalized,
                annot=True,
                fmt='.6f',
                cmap='YlOrRd',
                cbar_kws={'label': '정규화된 발생률 (인구 10만명당, 범죄 유형별 최댓값=1)'},
                linewidths=0.5,
                linecolor='gray'
            )
            plt.title('서울시 자치구별 범죄 발생률 히트맵 (인구 10만명당, 범죄 유형별 정규화)', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('범죄 유형', fontsize=12)
            plt.ylabel('자치구', fontsize=12)
            plt.tight_layout()
            
            # save 폴더에 저장
            heatmap_file_path = save_path / 'crime_heatmap.png'
            plt.savefig(heatmap_file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"범죄 발생률 히트맵 저장 완료: {heatmap_file_path}")
            logger.info("각 범죄 유형별로 최댓값을 1로 정규화 완료")
            logger.info(f"파일 존재 확인: {heatmap_file_path.exists()}")
            
            # 검거율 히트맵 생성
            logger.info("범죄 검거율 히트맵 생성 시작...")
            
            # 검거율 히트맵 파일 경로 초기화
            검거율_heatmap_file_path = None
            
            # 검거 컬럼 추출
            검거_cols = [col for col in crime_pop.columns if '검거' in col]
            
            if not 검거_cols:
                logger.warning("검거 컬럼을 찾을 수 없습니다. 검거율 히트맵을 건너뜁니다.")
            else:
                # 검거율 데이터프레임 생성
                검거율_data = pd.DataFrame(index=crime_pop[자치구_col].values)
                
                # 각 범죄 유형별로 검거율 계산
                for 발생_col in 발생_cols:
                    # 발생 컬럼명에서 ' 발생'을 제거하여 범죄 유형명 추출
                    범죄_유형 = 발생_col.replace(' 발생', '')
                    
                    # 해당 범죄 유형에 대응하는 검거 컬럼 찾기
                    검거_col = f"{범죄_유형} 검거"
                    
                    if 검거_col in 검거_cols:
                        발생_값 = crime_pop[발생_col].copy()
                        검거_값 = crime_pop[검거_col].copy()
                        
                        # 숫자형으로 변환
                        if 발생_값.dtype == 'object':
                            발생_값 = 발생_값.astype(str).str.replace(',', '').str.replace(' ', '')
                        발생_값 = pd.to_numeric(발생_값, errors='coerce').fillna(0)
                        
                        if 검거_값.dtype == 'object':
                            검거_값 = 검거_값.astype(str).str.replace(',', '').str.replace(' ', '')
                        검거_값 = pd.to_numeric(검거_값, errors='coerce').fillna(0)
                        
                        # 검거율 계산: 검거수 / 발생수 * 100 (%)
                        # 발생수가 0인 경우 처리 (0으로 나누기 방지)
                        발생_값_안전 = 발생_값.replace(0, np.nan)
                        검거율 = (검거_값 / 발생_값_안전) * 100  # %로 변환
                        검거율 = 검거율.fillna(0)  # 발생수가 0인 경우 검거율을 0으로 설정
                        
                        # 무한대나 null 값 처리
                        검거율 = 검거율.replace([np.inf, -np.inf], np.nan).fillna(0)
                        
                        검거율_data[범죄_유형] = 검거율.values
                    else:
                        logger.warning(f"{범죄_유형}에 대응하는 검거 컬럼을 찾을 수 없습니다: {검거_col}")
                
                # 검거율 데이터가 있는지 확인
                if 검거율_data.empty or len(검거율_data.columns) == 0:
                    logger.warning("검거율 데이터가 없습니다. 검거율 히트맵을 건너뜁니다.")
                else:
                    # 자치구를 인덱스로 설정
                    검거율_data.index = crime_pop[자치구_col].values
                    
                    # 최종 데이터 타입 확인 및 변환 (%로 이미 변환됨)
                    검거율_data = 검거율_data.astype(float)
                    검거율_data = 검거율_data.replace([np.inf, -np.inf], np.nan).fillna(0)
                    
                    # 검거율 히트맵 생성 (%로 표시, 정규화 없음)
                    plt.figure(figsize=(12, 10))
                    sns.heatmap(
                        검거율_data,
                        annot=True,
                        fmt='.2f',
                        cmap='YlGn',  # 연두색 계열 (Yellow-Green)
                        cbar_kws={'label': '검거율 (%)'},
                        linewidths=0.5,
                        linecolor='gray'
                    )
                    plt.title('서울시 자치구별 범죄 검거율 히트맵', fontsize=16, fontweight='bold', pad=20)
                    plt.xlabel('범죄 유형', fontsize=12)
                    plt.ylabel('자치구', fontsize=12)
                    plt.tight_layout()
                    
                    # save 폴더에 저장
                    검거율_heatmap_file_path = save_path / 'crime_arrest_rate_heatmap.png'
                    plt.savefig(검거율_heatmap_file_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    
                    logger.info(f"범죄 검거율 히트맵 저장 완료: {검거율_heatmap_file_path}")
                    logger.info(f"파일 존재 확인: {검거율_heatmap_file_path.exists()}")
            
            logger.info("🦝🦝제출 완료")
            
            result = {
                "message": "데이터 및 히트맵 저장 완료",
                "heatmap": {
                    "file_path": str(heatmap_file_path),
                    "file_exists": heatmap_file_path.exists()
                }
            }
            
            # 검거율 히트맵 정보 추가
            if 검거율_heatmap_file_path is not None:
                result["arrest_rate_heatmap"] = {
                    "file_path": str(검거율_heatmap_file_path),
                    "file_exists": 검거율_heatmap_file_path.exists()
                }
            
            # crime_with_gu.csv 저장 정보 추가 (저장된 경우만)
            if crime_file_path:
                result["crime_with_gu_csv"] = {
                    "file_path": str(crime_file_path),
                    "file_exists": crime_file_path.exists()
                }
            
            return result
            
        except ImportError as e:
            error_msg = f"히트맵 생성에 필요한 라이브러리가 없습니다: {e}. matplotlib, seaborn을 설치해주세요."
            logger.error(error_msg)
            raise ImportError(error_msg)
        except Exception as e:
            logger.error(f"히트맵 생성 중 오류 발생: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def get_data_by_type(self, data_type: str):
        """
        특정 타입의 데이터만 반환
        
        Args:
            data_type: 'cctv', 'crime', 'pop', 'crime_with_gu', 'crime_pop' 중 하나
        
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
            # pop의 경우 전체 행 반환
            return df_to_dict(df, head_rows=len(df))
        elif data_type.lower() == 'crime_with_gu':
            df = self.method.dataset.crime_with_gu
            if df is None:
                raise ValueError(f"{data_type} 데이터가 로드되지 않았습니다.")
            return df_to_dict(df)
        elif data_type.lower() == 'crime_pop':
            df = self.method.dataset.crime_pop
            if df is None:
                raise ValueError(f"{data_type} 데이터가 로드되지 않았습니다.")
            # crime_pop의 경우 전체 행 반환
            return df_to_dict(df, head_rows=len(df))
        elif data_type.lower() == 'cctv_crime_pop':
            df = self.method.dataset.cctv_crime_pop
            if df is None:
                raise ValueError(f"{data_type} 데이터가 로드되지 않았습니다.")
            # cctv_crime_pop의 경우 전체 행 반환
            return df_to_dict(df, head_rows=len(df))
        else:
            raise ValueError(f"지원하지 않는 데이터 타입입니다: {data_type}. 'cctv', 'crime', 'pop', 'crime_with_gu', 'crime_pop', 'cctv_crime_pop' 중 하나를 선택하세요.")

    def create_crime_map(self):
        """
        서울시 자치구별 범죄 데이터를 지도로 시각화
        
        Returns:
            dict: 저장된 지도 파일 경로 정보
        """
        logger.info("🦝🦝지도 생성 시작")
        
        # 전처리가 실행되지 않았다면 실행
        if self.method.dataset.cctv_crime_pop is None:
            logger.info("전처리가 실행되지 않았습니다. 전처리를 실행합니다.")
            self.preprocess()
        
        # cctv_crime_pop 데이터 가져오기
        cctv_crime_pop = self.method.dataset.cctv_crime_pop
        if cctv_crime_pop is None:
            raise ValueError("cctv_crime_pop 데이터가 없습니다. 전처리를 먼저 실행해주세요.")
        
        # save_path 확인 및 생성
        current_file = Path(__file__)
        save_path = current_file.parent / "save"
        save_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"저장 경로: {save_path}")
        
        # GeoJSON 파일 경로
        geo_json_path = current_file.parent / "data" / "kr-state.json"
        if not geo_json_path.exists():
            raise FileNotFoundError(f"GeoJSON 파일을 찾을 수 없습니다: {geo_json_path}")
        
        # GeoJSON 로드
        with open(geo_json_path, 'r', encoding='utf-8') as f:
            seoul_geo = json.load(f)
        
        logger.info("GeoJSON 파일 로드 완료")
        
        # 필수 컬럼 확인
        required_cols = ['자치구', '범죄발생', '범죄검거', 'CCTV']
        for col in required_cols:
            if col not in cctv_crime_pop.columns:
                raise ValueError(f"필수 컬럼을 찾을 수 없습니다: {col}")
        
        # 범죄발생 데이터 가져오기
        범죄발생 = cctv_crime_pop['범죄발생'].copy()
        if 범죄발생.dtype == 'object':
            범죄발생 = 범죄발생.astype(str).str.replace(',', '').str.replace(' ', '')
        범죄발생 = pd.to_numeric(범죄발생, errors='coerce').fillna(0)
        
        # 범죄발생 정규화 (0~1 사이)
        범죄발생_max = 범죄발생.max()
        if 범죄발생_max > 0:
            범죄발생_정규화 = 범죄발생 / 범죄발생_max
        else:
            범죄발생_정규화 = 범죄발생
        
        # 범죄검거 데이터 가져오기
        범죄검거 = cctv_crime_pop['범죄검거'].copy()
        if 범죄검거.dtype == 'object':
            범죄검거 = 범죄검거.astype(str).str.replace(',', '').str.replace(' ', '')
        범죄검거 = pd.to_numeric(범죄검거, errors='coerce').fillna(0)
        
        # 검거율 계산: (범죄검거 / 범죄발생) * 100
        범죄발생_안전 = 범죄발생.replace(0, np.nan)
        검거율 = (범죄검거 / 범죄발생_안전) * 100
        검거율 = 검거율.fillna(0).replace([np.inf, -np.inf], np.nan).fillna(0)
        
        # CCTV 수 가져오기
        cctv_data = cctv_crime_pop['CCTV'].copy()
        if cctv_data.dtype == 'object':
            cctv_data = cctv_data.astype(str).str.replace(',', '').str.replace(' ', '')
        cctv_data = pd.to_numeric(cctv_data, errors='coerce').fillna(0)
        
        # 데이터프레임 생성 (지도용)
        map_data = pd.DataFrame({
            '자치구': cctv_crime_pop['자치구'],
            '범죄발생_정규화': 범죄발생_정규화.values,
            'CCTV': cctv_data.values,
            '검거율': 검거율.values
        })
        
        # 지도 생성 (서울 중심 좌표)
        seoul_center = [37.5665, 126.9780]  # 서울시청 좌표
        m = folium.Map(location=seoul_center, zoom_start=11, tiles='OpenStreetMap')
        
        # Choropleth 레이어 추가 (범죄발생 정규화 값으로 색상 표시)
        folium.Choropleth(
            geo_data=seoul_geo,
            name="범죄 발생건수",
            data=map_data,
            columns=['자치구', '범죄발생_정규화'],
            key_on='feature.id',
            fill_color='YlOrRd',  # Yellow-Orange-Red 색상 팔레트
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="범죄 발생건수 (정규화)",
        ).add_to(m)
        
        # 각 자치구에 원형 마커 추가 (CCTV 수 = 크기, 검거율 = 색상)
        for idx, row in map_data.iterrows():
            자치구명 = row['자치구']
            cctv_count = row['CCTV']
            검거율 = row['검거율']
            
            # 자치구의 중심 좌표 찾기 (GeoJSON에서)
            중심_좌표 = None
            for feature in seoul_geo['features']:
                if feature['id'] == 자치구명:
                    # Polygon의 중심점 계산 (경계 좌표의 평균)
                    coords = feature['geometry']['coordinates'][0]
                    if coords:
                        lats = [coord[1] for coord in coords]
                        lngs = [coord[0] for coord in coords]
                        # 위도, 경도 순서로 반환 (folium은 [lat, lng] 형식)
                        중심_좌표 = [sum(lats) / len(lats), sum(lngs) / len(lngs)]
                    break
            
            if 중심_좌표:
                # CCTV 수에 따른 원 크기 (최소 8, 최대 50)
                cctv_max = map_data['CCTV'].max()
                cctv_min = map_data['CCTV'].min()
                if cctv_max > cctv_min:
                    radius = 8 + (cctv_count - cctv_min) / (cctv_max - cctv_min) * 42
                else:
                    radius = 25
                
                # 검거율에 따른 색상 그라데이션 (0~100%를 색상으로 매핑)
                # 검거율이 높을수록 초록색, 낮을수록 빨간색
                # RGB 값을 선형 보간으로 계산
                검거율_normalized = max(0, min(100, 검거율)) / 100.0
                
                if 검거율_normalized <= 0.5:
                    # 빨간색에서 주황색으로 (0~50%)
                    ratio = 검거율_normalized / 0.5
                    r = 255
                    g = int(165 * ratio)  # 0~165
                    b = 0
                else:
                    # 주황색에서 초록색으로 (50~100%)
                    ratio = (검거율_normalized - 0.5) / 0.5
                    r = int(255 * (1 - ratio))  # 255~0
                    g = 255
                    b = 0
                
                color = f'#{r:02x}{g:02x}{b:02x}'
                
                # 원형 마커 추가
                folium.CircleMarker(
                    location=중심_좌표,
                    radius=radius,
                    popup=folium.Popup(
                        f"<b>{자치구명}</b><br>"
                        f"CCTV 수: {int(cctv_count)}<br>"
                        f"검거율: {검거율:.2f}%<br>"
                        f"범죄발생(정규화): {row['범죄발생_정규화']:.3f}",
                        max_width=200
                    ),
                    tooltip=f"{자치구명} (CCTV: {int(cctv_count)}, 검거율: {검거율:.2f}%)",
                    color='black',
                    weight=2,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.8
                ).add_to(m)
        
        # 레이어 컨트롤 추가
        folium.LayerControl().add_to(m)
        
        # 지도 저장
        map_file_path = save_path / 'crime_map.html'
        m.save(str(map_file_path))
        
        logger.info(f"지도 저장 완료: {map_file_path}")
        logger.info("🦝🦝지도 생성 완료")
        
        return {
            "message": "지도 생성 완료",
            "file_path": str(map_file_path),
            "file_exists": map_file_path.exists()
        }