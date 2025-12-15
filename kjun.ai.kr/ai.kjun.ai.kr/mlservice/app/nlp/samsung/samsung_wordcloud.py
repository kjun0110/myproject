import re
import nltk
import logging
import pandas as pd

# Logger 먼저 정의
logger = logging.getLogger(__name__)

# NLTK 데이터 다운로드 확인
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logger.warning("NLTK punkt 데이터가 없습니다. 다운로드를 시도합니다...")
    try:
        nltk.download('punkt', quiet=True)
    except Exception as e:
        logger.error(f"NLTK punkt 데이터 다운로드 실패: {str(e)}")

# NLTK punkt_tab 데이터 다운로드 확인 (최신 NLTK 버전용)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    logger.warning("NLTK punkt_tab 데이터가 없습니다. 다운로드를 시도합니다...")
    try:
        nltk.download('punkt_tab', quiet=True)
    except Exception as e:
        logger.error(f"NLTK punkt_tab 데이터 다운로드 실패: {str(e)}")

from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from nltk.stem import PorterStemmer, LancasterStemmer, WordNetLemmatizer
from nltk.tag import pos_tag, untag
from nltk import Text, FreqDist
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # GUI 없이 사용 (서버 환경)
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import os

# KoNLPy의 Okt 형태소 분석기 import
try:
    from konlpy.tag import Okt
    logger.info("KoNLPy Okt 형태소 분석기를 사용합니다.")
except ImportError:
    logger.error("KoNLPy가 설치되지 않았습니다. pip install konlpy를 실행하세요.")
    raise


class SamsungWordcloud:

    def __init__(self):
        try:
            self.okt = Okt()
            logger.info("Okt 형태소 분석기 초기화 완료")
        except Exception as e:
            logger.error(f"Okt 형태소 분석기 초기화 실패: {str(e)}")
            raise RuntimeError(f"Okt 형태소 분석기 초기화 실패: {str(e)}. Java가 설치되어 있고 JAVA_HOME이 설정되어 있는지 확인하세요.")

    def text_process(self):
        freq_txt = self.find_freq()
        self.draw_wordcloud()
        return {
            '전처리 결과' : '완료',
            'freq_txt' : freq_txt,
        }

    def read_file(self):
        # 형태소 분석기 초기화 확인 (선택적)
        try:
            self.okt.pos('삼성전자 글로벌센터 전자사업부', stem=True)     #BoW만듦 빈도수 체크해서 인덱스 번호 부여
        except:
            pass
        # 현재 파일 기준으로 data 폴더 경로 찾기
        current_file = Path(__file__)
        data_path = current_file.parent.parent / "data" / "kr-Report_2018.txt"
        if not data_path.exists():
            raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")
        with open(data_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text
    
    def extract_hangeul(self, text: str):
        temp = text.replace('\n',' ')     #엔터를 제외
        tokenizer = re.compile(r'[^ ㄱ-힣]+')     #한글이 아닌거 제외,  r(정규표현식), + 한글자이상
        return tokenizer.sub('', temp)  # sub(repl, string) 형식으로 수정
    def change_token(self, texts):
        return word_tokenize(texts)
    
    def extract_noun(self):
        # 삼성전자의 스마트폰은 -> 삼성전자 스마트폰
        noun_tokens = []
        tokens = self.change_token(self.extract_hangeul(self.read_file()))
        for i in tokens:
            pos = self.okt.pos(i)
            # Okt 품사 태그: Noun
            temp = [j[0] for j in pos if j[1] == 'Noun']
            if len(''.join(temp)) > 1 :
                noun_tokens.append(''.join(temp))   #단어 앞에 띄어쓰기 추가
        texts = ' '.join(noun_tokens)
        logger.info(texts[:100])    # 100번째 단어까지 보여줘라
        return texts

    def read_stopword(self):
        # 형태소 분석기 초기화 확인 (선택적)
        try:
            self.okt.pos("삼성전자 글로벌센터 전자사업부", stem=True)
        except:
            pass
        # 현재 파일 기준으로 data 폴더 경로 찾기
        current_file = Path(__file__)
        stopwords_path = current_file.parent.parent / "data" / "stopwords.txt"
        if not stopwords_path.exists():
            logger.warning(f"불용어 파일을 찾을 수 없습니다: {stopwords_path}. 빈 문자열을 반환합니다.")
            return ""
        with open(stopwords_path, 'r', encoding='utf-8') as f:
            stopwords = f.read()
        return stopwords

    def remove_stopword(self):
        texts = self.extract_noun()
        tokens = self.change_token(texts)
        # print('------- 1 명사 -------')
        # print(texts[:30])
        stopwords = self.read_stopword()
        # print('------- 2 스톱 -------')
        # print(stopwords[:30])
        # print('------- 3 필터 -------')
        texts = [text for text in tokens
                 if text not in stopwords]
        # print(texts[:30])
        return texts
    
    def find_freq(self):
        texts = self.remove_stopword()
        freqtxt = pd.Series(dict(FreqDist(texts))).sort_values(ascending=False)
        logger.info(freqtxt[:30])
        return freqtxt

    def draw_wordcloud(self):
        texts = self.remove_stopword()
        
        # 현재 파일 기준으로 경로 찾기
        current_file = Path(__file__)
        data_path = current_file.parent.parent / "data"
        font_path = data_path / "D2Coding.ttf"
        
        # 폰트 파일이 없으면 기본 폰트 사용
        font_path_str = str(font_path) if font_path.exists() else None
        if font_path_str is None:
            logger.warning(f"폰트 파일을 찾을 수 없습니다: {font_path}. 기본 폰트를 사용합니다.")
        
        # WordCloud 생성 (고해상도 설정)
        width = 2000
        height = 2000
        if font_path_str:
            wcloud = WordCloud(font_path=font_path_str, 
                               width=width, 
                               height=height,
                               relative_scaling=0.2,
                               background_color='white',
                               max_words=500).generate(" ".join(texts))
        else:
            wcloud = WordCloud(width=width, 
                               height=height,
                               relative_scaling=0.2,
                               background_color='white',
                               max_words=500).generate(" ".join(texts))
        
        plt.figure(figsize=(20, 20), dpi=150)
        plt.imshow(wcloud, interpolation='bilinear')
        plt.axis('off')
        
        # save 폴더에 저장 (고해상도)
        save_path = current_file.parent.parent / "save"
        save_path.mkdir(parents=True, exist_ok=True)
        output_file = save_path / 'samsung_wordcloud.png'
        plt.savefig(output_file, dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return str(output_file)