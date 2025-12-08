from dataclasses import dataclass
import pandas as pd
import os

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

    def get_csv_path(self, fname: str) -> str:
        """CSV 파일의 전체 경로를 반환"""
        if self._dname:
            # dname이 설정되어 있으면 dname 기준
            return os.path.join(self._dname, fname)
        else:
            # dname이 없으면 현재 파일 기준 디렉토리 사용
            current_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(current_dir, fname)
