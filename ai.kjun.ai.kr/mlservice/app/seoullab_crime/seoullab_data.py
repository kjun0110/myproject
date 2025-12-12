from dataclasses import dataclass
from pathlib import Path
import pandas as pd


class SeoullabData(object):

        _fname: str = '' #file name
        _dname: str = str(Path(__file__).resolve().parent / "data")  # data path 절대경로
        _sname: str = str(Path(__file__).resolve().parent / "save")  # save path 절대경로로
        _cctv: pd.DataFrame = None
        _crime: pd.DataFrame = None
        _pop: pd.DataFrame = None
        _crime_with_gu: pd.DataFrame = None
        _crime_pop: pd.DataFrame = None
        _cctv_crime_pop: pd.DataFrame = None
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
        def crime_with_gu(self) -> pd.DataFrame: return self._crime_with_gu
        @crime_with_gu.setter
        def crime_with_gu(self, crime_with_gu): self._crime_with_gu = crime_with_gu

        @property
        def crime_pop(self) -> pd.DataFrame: return self._crime_pop
        @crime_pop.setter
        def crime_pop(self, crime_pop): self._crime_pop = crime_pop

        @property
        def cctv_crime_pop(self) -> pd.DataFrame: return self._cctv_crime_pop
        @cctv_crime_pop.setter
        def cctv_crime_pop(self, cctv_crime_pop): self._cctv_crime_pop = cctv_crime_pop

        @property
        def id(self) -> str: return self._id
        @id.setter
        def id(self, id): self._id = id

        @property
        def label(self) -> str: return self._label
        @label.setter
        def label(self, label): self._label = label


