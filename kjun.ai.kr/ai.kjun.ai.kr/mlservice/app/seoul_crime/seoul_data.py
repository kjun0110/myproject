from dataclasses import dataclass
from pathlib import Path
import pandas as pd


class SeoulData(object):

        _fname: str = '' #file name
        _dname: str = str(Path(__file__).resolve().parent / "data")  # data path 절대경로
        _sname: str = str(Path(__file__).resolve().parent / "save")  # save path 절대경로로
        _cctv: pd.DataFrame = None
        _crime: pd.DataFrame = None
        _pop: pd.DataFrame = None
        #비지도 _id: str = ''
        #비지도 _label: str = ''

        @property
        def fname(self) -> str: return self._fname
        @fname.setter
        def fname(self, fname): self._fname = fname

        @property
        def dname(self) -> str: return self._dname
        @dname.setter
        def dname(self, dname): self._dname = dname

        @property
        def sname(self) -> str: return self._sname
        @sname.setter
        def sname(self, sname): self._sname = sname

        @property
        def cctv(self) -> pd.DataFrame: return self._cctv
        @cctv.setter
        def cctv(self, cctv): self._cctv = cctv

        @property
        def crime(self) -> pd.DataFrame: return self._crime
        @crime.setter
        def crime(self, crime): self._crime = crime

        @property
        def pop(self) -> pd.DataFrame: return self._pop
        @pop.setter
        def pop(self, pop): self._pop = pop

        @property
        def id(self) -> str: return self._id
        @id.setter
        def id(self, id): self._id = id

        @property
        def label(self) -> str: return self._label
        @label.setter
        def label(self, label): self._label = label

        def read_csv(self, fname: str) -> pd.DataFrame:
            #csv 파일을 읽어와서 데이터프레임으로 반환
            filepath = Path(self._dname) / fname
            if not filepath.exists():
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")
            
            # 다중 헤더 구조 처리
            if fname == 'crime.csv':
                # crime.csv는 4행까지 헤더
                df = pd.read_csv(filepath, header=[0, 1, 2, 3])
            elif fname == 'pop.csv':
                # pop.csv는 3행까지 헤더
                df = pd.read_csv(filepath, header=[0, 1, 2])
            else:
                return pd.read_csv(filepath)
            
            # MultiIndex를 평탄화하여 하나의 컬럼명으로 만들기
            new_columns = []
            for col_tuple in df.columns.values:
                # 각 레벨의 값을 리스트로 만들고, 중복 제거 및 빈 값 제거
                parts = [str(col).strip() for col in col_tuple 
                        if str(col) != 'nan' and str(col).strip() and str(col) != '']
                # 중복 제거 (순서 유지)
                seen = set()
                unique_parts = []
                for part in parts:
                    if part not in seen:
                        seen.add(part)
                        unique_parts.append(part)
                # '_'로 연결
                new_col = '_'.join(unique_parts) if unique_parts else 'Unnamed'
                new_columns.append(new_col)
            df.columns = new_columns
            return df

        def read_excel(self, fname: str) -> pd.DataFrame:
            #xlsx 파일을 읽어와서 데이터프레임으로 반환
            filepath = Path(self._dname) / fname
            if not filepath.exists():
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")
            try:
                # cctv.xlsx는 1행이 헤더, 2행은 합계(건너뛰기), 3행부터 데이터
                if fname == 'cctv.xlsx':
                    # 헤더 없이 읽기
                    df = pd.read_excel(filepath, engine='openpyxl', header=None)
                    # 1행(인덱스 1)을 컬럼명으로 사용 (0행은 단위 정보)
                    if len(df) > 1:
                        # 1행의 값들을 컬럼명으로 설정
                        new_columns = [str(val).strip() if not pd.isna(val) else f'Unnamed_{i}' 
                                     for i, val in enumerate(df.iloc[1])]
                        df.columns = new_columns
                        # 0행(단위 정보)과 1행(헤더였던 행) 제거, 2행부터 시작
                        df = df.iloc[2:].reset_index(drop=True)
                        # 합계 행 제거 - '구분' 컬럼이 '계' 또는 '합계'인 경우 (첫 번째 컬럼 제거 전에 확인)
                        if len(df) > 0 and '구분' in df.columns:
                            df = df[df['구분'].astype(str).str.strip() != '계'].reset_index(drop=True)
                            df = df[df['구분'].astype(str).str.strip() != '합계'].reset_index(drop=True)
                        # 첫 번째 컬럼이 비어있거나 'Unnamed'로 시작하면 제거
                        if len(df.columns) > 0 and (df.columns[0].startswith('Unnamed') or df.columns[0].strip() == '' or pd.isna(df.columns[0])):
                            df = df.iloc[:, 1:].copy()
                    return df
                else:
                    return pd.read_excel(filepath, engine='openpyxl')
            except ImportError:
                raise ImportError("openpyxl 패키지가 필요합니다. 'pip install openpyxl'을 실행해주세요.")


