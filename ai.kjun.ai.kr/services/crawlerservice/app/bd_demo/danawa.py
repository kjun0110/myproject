"""
다나와 메탈시계 제품 정보 크롤러
정적 크롤링을 사용하여 prod_name, prod_meta, low_price 정보를 추출합니다.
"""

import requests
from bs4 import BeautifulSoup
import json


def crawl_danawa_products():
    """
    다나와 메탈시계 제품 목록에서 제품 정보를 크롤링합니다.
    
    Returns:
        list: 제품 정보를 담은 딕셔너리 리스트
    """
    url = "https://prod.danawa.com/list/?cate=18349533"
    
    # User-Agent 헤더 추가 (봇 차단 방지)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 웹페이지 요청
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 제품 데이터 저장할 리스트
        products_data = []
        
        # 제품 목록 찾기
        # 다나와의 일반적인 구조: product_list 또는 prod_list 클래스
        product_list = soup.select('div.product_list')
        
        if not product_list:
            # 대체 셀렉터 시도
            product_list = soup.select('div.prod_list')
        
        if not product_list:
            # 다른 대체 셀렉터
            product_list = soup.select('ul.product_list')
        
        if product_list:
            # 제품 리스트 내의 각 제품 아이템 찾기
            products = product_list[0].select('li.prod_item, div.prod_item')
            
            for idx, product in enumerate(products, 1):
                try:
                    # prod_name 추출
                    name_element = product.select_one('.prod_name, .prod_name a, a.prod_name')
                    prod_name = name_element.get_text(strip=True) if name_element else "N/A"
                    
                    # prod_meta 추출
                    meta_element = product.select_one('.prod_meta, .spec_list')
                    prod_meta = meta_element.get_text(strip=True) if meta_element else "N/A"
                    
                    # low_price 추출
                    price_element = product.select_one('.low_price, .price_sect strong, .price strong')
                    low_price = price_element.get_text(strip=True) if price_element else "N/A"
                    
                    # 제품 정보를 딕셔너리로 저장
                    product_info = {
                        "index": idx,
                        "prod_name": prod_name,
                        "prod_meta": prod_meta,
                        "low_price": low_price
                    }
                    
                    products_data.append(product_info)
                    
                except Exception as e:
                    print(f"제품 {idx} 파싱 중 오류 발생: {e}")
                    continue
        else:
            print("제품 목록을 찾을 수 없습니다.")
            
            # 디버깅을 위해 페이지 구조 일부 출력
            print("\n=== 페이지 구조 확인 ===")
            # 제품 관련 클래스 찾기
            prod_classes = soup.find_all(class_=lambda x: x and 'prod' in x.lower(), limit=10)
            for i, elem in enumerate(prod_classes):
                print(f"요소 {i+1}: {elem.get('class', 'class 없음')}")
        
        return products_data
        
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
    print("다나와 메탈시계 제품 크롤링 시작...\n")
    
    # 제품 데이터 크롤링
    products_data = crawl_danawa_products()
    
    if products_data:
        # JSON 형태로 출력 (한글이 깨지지 않도록 ensure_ascii=False 설정)
        print(json.dumps(products_data, ensure_ascii=False, indent=2))
        print(f"\n총 {len(products_data)}개의 제품 정보를 크롤링했습니다.")
    else:
        print("크롤링된 데이터가 없습니다.")


if __name__ == "__main__":
    main()

