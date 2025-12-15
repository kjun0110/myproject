# ************
# NLTK 자연어 처리 패키지
# ************
"""
https://datascienceschool.net/view-notebook/118731eec74b4ad3bdd2f89bab077e1b/
NLTK(Natural Language Toolkit) 패키지는 
교육용으로 개발된 자연어 처리 및 문서 분석용 파이썬 패키지다. 
다양한 기능 및 예제를 가지고 있으며 실무 및 연구에서도 많이 사용된다.
NLTK 패키지가 제공하는 주요 기능은 다음과 같다.
말뭉치
토큰 생성
형태소 분석
품사 태깅
"""

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from nltk.stem import PorterStemmer, LancasterStemmer, WordNetLemmatizer
from nltk.tag import pos_tag, untag
from nltk import Text, FreqDist
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import os


class NLPService:
    """
    NLTK를 사용한 자연어 처리 서비스 클래스
    
    주요 기능:
    - 말뭉치 관리
    - 토큰 생성
    - 형태소 분석
    - 품사 태깅
    - 텍스트 분석
    - 워드클라우드 생성
    """
    
    def __init__(self, download_data=True):
        """
        NLPService 초기화
        
        Args:
            download_data (bool): NLTK 데이터 다운로드 여부
        """
        if download_data:
            # 필요한 NLTK 데이터 다운로드
            required_data = [
                'book',  # 말뭉치 데이터
                'punkt',  # 토큰화용
                'averaged_perceptron_tagger_eng',  # POS tagging용
                'wordnet',  # lemmatization용
                'stopwords'  # 불용어 리스트
            ]
            
            for data in required_data:
                try:
                    nltk.download(data, quiet=True)
                except Exception as e:
                    # 이미 다운로드된 경우 무시
                    pass
        
        # 토크나이저 초기화
        self.regex_tokenizer = RegexpTokenizer("[\w]+")
        
        # 형태소 분석기 초기화
        self.porter_stemmer = PorterStemmer()
        self.lancaster_stemmer = LancasterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        
        # 말뭉치 데이터 저장
        self.corpus_data = {}
        self.text_objects = {}
    
    # *********
    # 말뭉치 관리
    # *********
    
    def get_corpus_fileids(self, corpus_name='gutenberg'):
        """
        말뭉치 파일 ID 목록 반환
        
        Args:
            corpus_name (str): 말뭉치 이름 (기본값: 'gutenberg')
            
        Returns:
            list: 파일 ID 목록
        """
        corpus = getattr(nltk.corpus, corpus_name, None)
        if corpus:
            return corpus.fileids()
        return []
    
    def load_corpus(self, corpus_name, fileid):
        """
        말뭉치 파일 로드
        
        Args:
            corpus_name (str): 말뭉치 이름
            fileid (str): 파일 ID
            
        Returns:
            str: 말뭉치 원문 데이터
        """
        corpus = getattr(nltk.corpus, corpus_name, None)
        if corpus:
            raw_text = corpus.raw(fileid)
            self.corpus_data[f"{corpus_name}_{fileid}"] = raw_text
            return raw_text
        return None
    
    def get_emma_corpus(self):
        """
        제인 오스틴의 엠마 말뭉치 로드
        
        Returns:
            str: 엠마 원문 데이터
        """
        return self.load_corpus('gutenberg', 'austen-emma.txt')
    
    # ************
    # 토큰 생성
    # ************
    
    def tokenize_sentences(self, text):
        """
        문장 단위 토큰화
        
        Args:
            text (str): 입력 텍스트
            
        Returns:
            list: 문장 토큰 리스트
        """
        return sent_tokenize(text)
    
    def tokenize_words(self, text):
        """
        단어 단위 토큰화
        
        Args:
            text (str): 입력 텍스트
            
        Returns:
            list: 단어 토큰 리스트
        """
        return word_tokenize(text)
    
    def tokenize_regex(self, text, pattern="[\w]+"):
        """
        정규표현식을 사용한 토큰화
        
        Args:
            text (str): 입력 텍스트
            pattern (str): 정규표현식 패턴
            
        Returns:
            list: 토큰 리스트
        """
        tokenizer = RegexpTokenizer(pattern)
        return tokenizer.tokenize(text)
    
    # ***************
    # 형태소 분석
    # ***************
    
    def stem_porter(self, words):
        """
        Porter Stemmer를 사용한 어간 추출
        
        Args:
            words (list or str): 단어 또는 단어 리스트
            
        Returns:
            list: 어간 추출된 단어 리스트
        """
        if isinstance(words, str):
            words = [words]
        return [self.porter_stemmer.stem(w) for w in words]
    
    def stem_lancaster(self, words):
        """
        Lancaster Stemmer를 사용한 어간 추출
        
        Args:
            words (list or str): 단어 또는 단어 리스트
            
        Returns:
            list: 어간 추출된 단어 리스트
        """
        if isinstance(words, str):
            words = [words]
        return [self.lancaster_stemmer.stem(w) for w in words]
    
    def lemmatize(self, words, pos=None):
        """
        원형 복원 (Lemmatization)
        
        Args:
            words (list or str): 단어 또는 단어 리스트
            pos (str): 품사 태그 (선택사항)
            
        Returns:
            list: 원형 복원된 단어 리스트
        """
        if isinstance(words, str):
            words = [words]
        
        if pos:
            return [self.lemmatizer.lemmatize(w, pos=pos) for w in words]
        else:
            return [self.lemmatizer.lemmatize(w) for w in words]
    
    # **********
    # POS tagging
    # **********
    
    def get_pos_tag_info(self, tag):
        """
        품사 태그 정보 조회
        
        Args:
            tag (str): 품사 태그
            
        Returns:
            str: 품사 태그 설명
        """
        nltk.help.upenn_tagset(tag)
    
    def pos_tag(self, tokens):
        """
        품사 태깅
        
        Args:
            tokens (list): 토큰 리스트
            
        Returns:
            list: (토큰, 품사) 튜플 리스트
        """
        return pos_tag(tokens)
    
    def extract_nouns(self, text):
        """
        명사만 추출
        
        Args:
            text (str): 입력 텍스트
            
        Returns:
            list: 명사 토큰 리스트
        """
        tokens = self.tokenize_words(text)
        tagged_list = self.pos_tag(tokens)
        return [t[0] for t in tagged_list if t[1] == "NN"]
    
    def remove_tags(self, tagged_list):
        """
        품사 태그 제거
        
        Args:
            tagged_list (list): (토큰, 품사) 튜플 리스트
            
        Returns:
            list: 토큰 리스트
        """
        return untag(tagged_list)
    
    def create_pos_tokenizer(self, text):
        """
        품사 정보를 포함한 토크나이저 생성
        
        Args:
            text (str): 입력 텍스트
            
        Returns:
            list: 품사가 포함된 토큰 리스트 (형식: "토큰/품사")
        """
        tokens = self.tokenize_words(text)
        tagged_list = self.pos_tag(tokens)
        return ["/".join(p) for p in tagged_list]
    
    # ***********
    # Text 클래스
    # ***********
    
    def create_text_object(self, tokens, name="Text"):
        """
        NLTK Text 객체 생성
        
        Args:
            tokens (list): 토큰 리스트
            name (str): 텍스트 이름
            
        Returns:
            Text: NLTK Text 객체
        """
        text_obj = Text(tokens, name=name)
        self.text_objects[name] = text_obj
        return text_obj
    
    def plot_word_frequency(self, text_obj, num_words=20):
        """
        단어 빈도 그래프 그리기
        
        Args:
            text_obj (Text): NLTK Text 객체
            num_words (int): 표시할 단어 수
        """
        text_obj.plot(num_words)
        plt.show()
    
    def plot_dispersion(self, text_obj, words):
        """
        단어 분산 플롯
        
        Args:
            text_obj (Text): NLTK Text 객체
            words (list): 분석할 단어 리스트
        """
        text_obj.dispersion_plot(words)
    
    def find_concordance(self, text_obj, word, lines=5):
        """
        단어 사용 위치 찾기
        
        Args:
            text_obj (Text): NLTK Text 객체
            word (str): 찾을 단어
            lines (int): 표시할 줄 수
        """
        text_obj.concordance(word, lines=lines)
    
    def find_similar_words(self, text_obj, word, num=10):
        """
        유사한 문맥에서 사용된 단어 찾기
        
        Args:
            text_obj (Text): NLTK Text 객체
            word (str): 기준 단어
            num (int): 반환할 단어 수
            
        Returns:
            list: 유사 단어 리스트
        """
        return text_obj.similar(word, num)
    
    def find_collocations(self, text_obj, num=10):
        """
        연어(collocation) 찾기
        
        Args:
            text_obj (Text): NLTK Text 객체
            num (int): 반환할 연어 수
        """
        text_obj.collocations(num)
    
    # ***********
    # FreqDist
    # ***********
    
    def create_freq_dist(self, tokens):
        """
        빈도 분포 객체 생성
        
        Args:
            tokens (list): 토큰 리스트
            
        Returns:
            FreqDist: 빈도 분포 객체
        """
        return FreqDist(tokens)
    
    def get_freq_stats(self, freq_dist, word):
        """
        단어 빈도 통계 조회
        
        Args:
            freq_dist (FreqDist): 빈도 분포 객체
            word (str): 조회할 단어
            
        Returns:
            tuple: (전체 단어 수, 단어 출현 횟수, 단어 출현 확률)
        """
        return freq_dist.N(), freq_dist[word], freq_dist.freq(word)
    
    def get_most_common(self, freq_dist, num=10):
        """
        가장 빈도가 높은 단어 조회
        
        Args:
            freq_dist (FreqDist): 빈도 분포 객체
            num (int): 반환할 단어 수
            
        Returns:
            list: (단어, 빈도) 튜플 리스트
        """
        return freq_dist.most_common(num)
    
    def extract_proper_nouns(self, text, stopwords=None):
        """
        고유명사 추출 (NNP 태그)
        
        Args:
            text (str): 입력 텍스트
            stopwords (list): 제외할 단어 리스트
            
        Returns:
            FreqDist: 고유명사 빈도 분포 객체
        """
        if stopwords is None:
            stopwords = ["Mr.", "Mrs.", "Miss", "Mr", "Mrs", "Dear"]
        
        tokens = self.tokenize_regex(text)
        tagged_list = self.pos_tag(tokens)
        names_list = [
            t[0] for t in tagged_list 
            if t[1] == "NNP" and t[0] not in stopwords
        ]
        return self.create_freq_dist(names_list)
    
    # ***********
    # 워드클라우드
    # ***********
    
    def generate_wordcloud(self, freq_dist, width=1000, height=600, 
                          background_color="white", random_state=0, save_path=None):
        """
        워드클라우드 생성 및 저장
        
        Args:
            freq_dist (FreqDist): 빈도 분포 객체
            width (int): 이미지 너비
            height (int): 이미지 높이
            background_color (str): 배경색
            random_state (int): 랜덤 시드
            save_path (str, optional): 저장 경로 
                - None: 저장하지 않음
                - "auto": 자동 생성 (타임스탬프 포함)
                - "fixed": 고정 파일명으로 저장 (덮어쓰기)
                - str: 지정된 경로로 저장
            
        Returns:
            tuple: (WordCloud 객체, 저장된 파일 경로 또는 None)
        """
        wc = WordCloud(
            width=width, 
            height=height, 
            background_color=background_color, 
            random_state=random_state
        )
        wordcloud = wc.generate_from_frequencies(freq_dist)
        
        # 이미지 저장 처리
        saved_path = None
        if save_path == "auto":
            # 현재 파일의 위치를 기준으로 save 디렉토리 경로 생성
            current_file = Path(__file__)
            save_dir = current_file.parent.parent / "save"
            
            # save 디렉토리가 없으면 생성
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # 파일명 생성 (타임스탬프 포함)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"emma_wordcloud_{timestamp}.png"
            save_path_obj = save_dir / filename
            saved_path = str(save_path_obj)
        elif save_path == "fixed":
            # 고정 파일명으로 저장 (덮어쓰기)
            current_file = Path(__file__)
            save_dir = current_file.parent.parent / "save"
            
            # save 디렉토리가 없으면 생성
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # 고정 파일명
            filename = "emma_wordcloud.png"
            save_path_obj = save_dir / filename
            saved_path = str(save_path_obj)
        elif save_path is not None and isinstance(save_path, str):
            # 지정된 경로로 저장
            save_path_obj = Path(save_path)
            # 디렉토리가 없으면 생성
            save_path_obj.parent.mkdir(parents=True, exist_ok=True)
            saved_path = str(save_path_obj)
        
        # 이미지 저장 (save_path가 None이 아니고 저장 경로가 지정된 경우만)
        if saved_path:
            wordcloud.to_file(saved_path)
        
        return wordcloud, saved_path
    
    def plot_wordcloud(self, freq_dist, width=1000, height=600, 
                      background_color="white", random_state=0):
        """
        워드클라우드 시각화
        
        Args:
            freq_dist (FreqDist): 빈도 분포 객체
            width (int): 이미지 너비
            height (int): 이미지 높이
            background_color (str): 배경색
            random_state (int): 랜덤 시드
        """
        wc, saved_path = self.generate_wordcloud(
            freq_dist, width, height, background_color, random_state
        )
        print(f"워드클라우드 이미지 저장됨: {saved_path}")
        plt.imshow(wc)
        plt.axis("off")
        plt.show()
    
    # ***********
    # 통합 분석 메서드
    # ***********
    
    def analyze_text(self, text, corpus_name=None, fileid=None):
        """
        텍스트 전체 분석 수행
        
        Args:
            text (str): 분석할 텍스트
            corpus_name (str): 말뭉치 이름 (선택사항)
            fileid (str): 파일 ID (선택사항)
            
        Returns:
            dict: 분석 결과 딕셔너리
        """
        # 토큰화
        sentences = self.tokenize_sentences(text)
        words = self.tokenize_words(text)
        
        # 품사 태깅
        pos_tags = self.pos_tag(words)
        
        # 명사 추출
        nouns = self.extract_nouns(text)
        
        # 빈도 분포
        freq_dist = self.create_freq_dist(words)
        
        # 고유명사 추출
        proper_nouns = self.extract_proper_nouns(text)
        
        return {
            'sentences': sentences,
            'words': words,
            'pos_tags': pos_tags,
            'nouns': nouns,
            'freq_dist': freq_dist,
            'proper_nouns': proper_nouns,
            'total_words': freq_dist.N(),
            'unique_words': len(freq_dist)
        }


# 사용 예제
if __name__ == "__main__":
    # 서비스 인스턴스 생성
    nlp_service = NLPService()
    
    # 엠마 말뭉치 로드
    emma_raw = nlp_service.get_emma_corpus()
    print(emma_raw[:1302])
    
    # 토큰 생성 예제
    sentences = nlp_service.tokenize_sentences(emma_raw[:1000])
    print(sentences[3] if len(sentences) > 3 else "")
    
    words = nlp_service.tokenize_words(emma_raw[50:100])
    print(words)
    
    regex_tokens = nlp_service.tokenize_regex(emma_raw[50:100])
    print(regex_tokens)
    
    # 형태소 분석 예제
    test_words = ['lives', 'crying', 'flies', 'dying']
    porter_stems = nlp_service.stem_porter(test_words)
    print(f"Porter Stemming: {porter_stems}")
    
    lancaster_stems = nlp_service.stem_lancaster(test_words)
    print(f"Lancaster Stemming: {lancaster_stems}")
    
    lemmas = nlp_service.lemmatize(test_words)
    print(f"Lemmatization: {lemmas}")
    
    lemma_verb = nlp_service.lemmatize("dying", pos="v")
    print(f"Lemmatization (verb): {lemma_verb}")
    
    # 품사 태깅 예제
    sentence = "Emma refused to permit us to obtain the refuse permit"
    tagged_list = nlp_service.pos_tag(nlp_service.tokenize_words(sentence))
    print(f"POS Tags: {tagged_list}")
    
    nouns = nlp_service.extract_nouns(sentence)
    print(f"Nouns: {nouns}")
    
    # Text 객체 생성 및 분석
    emma_tokens = nlp_service.tokenize_regex(emma_raw)
    emma_text = nlp_service.create_text_object(emma_tokens, name="Emma")
    
    # 빈도 분포 분석
    proper_nouns_fd = nlp_service.extract_proper_nouns(emma_raw)
    stats = nlp_service.get_freq_stats(proper_nouns_fd, "Emma")
    print(f"Emma stats: Total={stats[0]}, Count={stats[1]}, Freq={stats[2]}")
    
    most_common = nlp_service.get_most_common(proper_nouns_fd, 5)
    print(f"Most common: {most_common}")
    
    # 워드클라우드 생성
    nlp_service.plot_wordcloud(proper_nouns_fd)
