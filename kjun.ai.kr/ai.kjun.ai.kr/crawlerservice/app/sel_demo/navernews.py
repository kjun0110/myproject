"""
네이버 뉴스 검색 크롤러 (Selenium 사용)
ESG 키워드로 네이버 뉴스를 검색하여 제목과 관련 정보를 추출합니다.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import json
import time


def crawl_navernews(keyword="esg"):
    """
    네이버 뉴스 검색 결과를 크롤링합니다.
    
    Args:
        keyword (str): 검색 키워드 (기본값: "esg")
    
    Returns:
        list: 뉴스 정보를 담은 딕셔너리 리스트
    """
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 브라우저 창 숨기기
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = None
    news_data = []
    
    try:
        # Chrome 드라이버 초기화
        driver = webdriver.Chrome(options=chrome_options)
        
        # 네이버 뉴스 검색 페이지 접속 (기간 필터 없음)
        url = (
            f"https://search.naver.com/search.naver?"
            f"ssc=tab.news.all&where=news&sm=tab_jum&query={keyword}"
        )
        
        print(f"검색 키워드: {keyword}")
        print(f"URL: {url}\n")
        
        driver.get(url)
        
        # 페이지 로딩 대기
        time.sleep(2)
        
        # 뉴스 기사 요소들 찾기
        try:
            # 첫 번째 셀렉터: sds-comps-horizontal-layout sds-comps-inline-layout sds-comps-profile-info-title
            profile_titles = driver.find_elements(
                By.CSS_SELECTOR, 
                ".sds-comps-horizontal-layout.sds-comps-inline-layout.sds-comps-profile-info-title"
            )
            
            for idx, element in enumerate(profile_titles, 1):
                try:
                    text = element.text.strip()
                    if text:
                        news_data.append({
                            "index": idx,
                            "type": "profile_info_title",
                            "content": text
                        })
                except Exception as e:
                    print(f"프로필 제목 {idx} 추출 중 오류: {e}")
            
            # 두 번째 셀렉터: fender-ui_228e3bd1 xaRANlI1WEmTnsgGH3eP
            fender_elements = driver.find_elements(
                By.CSS_SELECTOR,
                ".fender-ui_228e3bd1.xaRANlI1WEmTnsgGH3eP"
            )
            
            for idx, element in enumerate(fender_elements, 1):
                try:
                    text = element.text.strip()
                    if text:
                        news_data.append({
                            "index": idx + len(profile_titles),
                            "type": "fender_ui",
                            "content": text
                        })
                except Exception as e:
                    print(f"Fender UI {idx} 추출 중 오류: {e}")
            
            # 추가: 일반 뉴스 제목 추출 (대체 방법)
            if not news_data:
                print("지정된 클래스를 찾지 못했습니다. 대체 셀렉터를 시도합니다.")
                
                # 뉴스 제목 요소 찾기
                news_titles = driver.find_elements(By.CSS_SELECTOR, ".news_tit")
                
                for idx, title in enumerate(news_titles, 1):
                    try:
                        text = title.text.strip()
                        href = title.get_attribute('href')
                        
                        news_data.append({
                            "index": idx,
                            "type": "news_title",
                            "title": text,
                            "url": href
                        })
                    except Exception as e:
                        print(f"뉴스 제목 {idx} 추출 중 오류: {e}")
        
        except Exception as e:
            print(f"요소 검색 중 오류 발생: {e}")
        
        return news_data
        
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        return []
    
    finally:
        # 드라이버 종료
        if driver:
            driver.quit()


def main():
    """
    메인 함수: 크롤링을 실행하고 결과를 JSON 형태로 출력합니다.
    """
    print("네이버 뉴스 검색 크롤링 시작 (키워드: ESG, 기간: 전체)...\n")
    
    # 뉴스 데이터 크롤링 (기간 필터 없음)
    news_data = crawl_navernews("esg")
    
    if news_data:
        # JSON 형태로 출력 (한글이 깨지지 않도록 ensure_ascii=False 설정)
        print(json.dumps(news_data, ensure_ascii=False, indent=2))
        print(f"\n총 {len(news_data)}개의 뉴스 정보를 크롤링했습니다.")
    else:
        print("크롤링된 데이터가 없습니다.")


if __name__ == "__main__":
    main()

