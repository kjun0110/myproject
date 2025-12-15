FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# LightGBM을 위한 시스템 라이브러리, 한글 폰트, Java 설치
RUN apt-get update && apt-get install -y \
    libgomp1 \
    fonts-nanum \
    fontconfig \
    default-jdk \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -fv

# JAVA_HOME 환경변수 설정
ENV JAVA_HOME=/usr/lib/jvm/default-java

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NLTK 데이터 다운로드 (punkt, punkt_tab)
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"

# 앱 코드 복사
COPY app .

# Uvicorn 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9010"]

