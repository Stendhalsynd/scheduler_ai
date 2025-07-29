import requests
from bs4 import BeautifulSoup
import urllib.parse
import argparse # argparse 라이브러리 추가

def scrape_google_news(query):
    """지정된 쿼리로 구글 뉴스를 스크레이핑하는 함수"""
    try:
        # 구글 뉴스 URL 생성 (한글 쿼리 인코딩)
        encoded_query = urllib.parse.quote_plus(query)
        URL = f"https://news.google.com/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"

        # HTTP 요청 보내기
        response = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # 오류 발생 시 예외 처리

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')

        # 뉴스 기사들을 담고 있는 'article' 태그 찾기
        articles = soup.find_all('article')

        print(f"'{query}'에 대한 뉴스 검색 결과 (최대 10개):\n" + "="*50)

        if not articles:
            print("검색된 뉴스 기사가 없습니다.")
            return

        # 각 기사에서 제목과 링크 추출 (최대 10개)
        for i, article in enumerate(articles[:10]):
            # 제목 추출
            title_tag = article.find('h4')
            title = title_tag.text if title_tag else "제목을 찾을 수 없음"
            
            # 링크 추출
            link_tag = article.find('a', href=True)
            raw_link = link_tag['href'] if link_tag else ''
            link = "https://news.google.com" + raw_link[1:] if raw_link.startswith('.') else "링크를 찾을 수 없음"
            
            print(f"[{i+1}] {title}")
            print(f"  - 링크: {link}\n")

    except requests.exceptions.RequestException as e:
        print(f"HTTP 요청 중 오류 발생: {e}")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    # 커맨드 라인 인자를 받기 위한 설정
    parser = argparse.ArgumentParser(description="구글 뉴스에서 특정 키워드로 최신 뉴스를 검색합니다.")
    parser.add_argument('query', type=str, help='검색할 뉴스 키워드를 입력하세요.')
    
    args = parser.parse_args()
    
    # 입력받은 쿼리로 함수 실행
    scrape_google_news(args.query)