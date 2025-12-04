"""
Bugs Music 실시간 차트 크롤러
정적 크롤링을 사용하여 title, artist, album 정보를 추출합니다.
"""

import requests
from bs4 import BeautifulSoup
import json


def crawl_bugs_chart():
    """
    Bugs Music 실시간 차트에서 곡 정보를 크롤링합니다.
    
    Returns:
        list: 곡 정보를 담은 딕셔너리 리스트
    """
    url = "https://music.bugs.co.kr/chart/track/realtime/total"
    
    # User-Agent 헤더 추가 (일부 사이트는 봇 접근을 차단할 수 있음)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 웹페이지 요청
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 차트 데이터 저장할 리스트
        chart_data = []
        
        # Bugs Music의 차트 테이블 찾기
        # 실제 구조에 따라 셀렉터를 조정해야 할 수 있습니다
        chart_table = soup.select('table.list.trackList.byChart')
        
        if not chart_table:
            # 대체 셀렉터 시도
            chart_table = soup.select('table.trackList')
        
        if chart_table:
            # 테이블의 각 행(tr) 순회
            rows = chart_table[0].select('tbody tr')
            
            for idx, row in enumerate(rows, 1):
                try:
                    # title 정보 추출
                    title_element = row.select_one('p.title a')
                    title = title_element.get_text(strip=True) if title_element else "N/A"
                    
                    # artist 정보 추출
                    artist_element = row.select_one('p.artist a')
                    artist = artist_element.get_text(strip=True) if artist_element else "N/A"
                    
                    # album 정보 추출
                    album_element = row.select_one('a.album')
                    album = album_element.get_text(strip=True) if album_element else "N/A"
                    
                    # 곡 정보를 딕셔너리로 저장
                    song_info = {
                        "rank": idx,
                        "title": title,
                        "artist": artist,
                        "album": album
                    }
                    
                    chart_data.append(song_info)
                    
                except Exception as e:
                    print(f"행 {idx} 파싱 중 오류 발생: {e}")
                    continue
        else:
            print("차트 테이블을 찾을 수 없습니다.")
            
            # 디버깅을 위해 페이지 구조 일부 출력
            print("\n=== 페이지 구조 확인 ===")
            tables = soup.find_all('table', limit=3)
            for i, table in enumerate(tables):
                print(f"테이블 {i+1}: {table.get('class', 'class 없음')}")
        
        return chart_data
        
    except requests.RequestException as e:
        print(f"웹페이지 요청 중 오류 발생: {e}")
        return []
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        return []


def main():
    """
    메인 함수: 크롤링을 실행하고 결과를 JSON 형태로 출력합니다.
    """
    print("Bugs Music 실시간 차트 크롤링 시작...\n")
    
    # 차트 데이터 크롤링
    chart_data = crawl_bugs_chart()
    
    if chart_data:
        # JSON 형태로 출력 (한글이 깨지지 않도록 ensure_ascii=False 설정)
        print(json.dumps(chart_data, ensure_ascii=False, indent=2))
        print(f"\n총 {len(chart_data)}곡의 정보를 크롤링했습니다.")
    else:
        print("크롤링된 데이터가 없습니다.")


if __name__ == "__main__":
    main()

