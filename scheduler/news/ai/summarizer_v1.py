import requests
from bs4 import BeautifulSoup
import urllib.parse
import argparse
import re
import os
import google.generativeai as genai
from dotenv import load_dotenv # 1. 라이브러리 불러오기

# --- 1단계: 뉴스 스크레이핑 함수 (수정됨) ---
def scrape_google_news(query):
    """지정된 쿼리로 구글 뉴스 헤드라인을 스크레이핑하는 함수 (개선된 방식)"""
    print(f"'{query}' 키워드로 최신 뉴스를 검색합니다...")
    try:
        # 검색어를 URL 인코딩합니다.
        encoded_query = urllib.parse.quote_plus(query)
        
        # www.google.com의 뉴스 검색(tbm=nws) URL을 사용합니다.
        URL = f"https://www.google.com/search?q={encoded_query}&tbm=nws&hl=ko&gl=KR"
        
        # 헤더를 추가하여 요청이 차단되는 것을 방지합니다.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(URL, headers=headers)
        # 요청이 성공했는지 확인합니다.
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 뉴스 헤드라인은 'MBeuO' 클래스를 가진 div 태그에 포함되어 있습니다.
        headline_tags = soup.find_all('div', class_='MBeuO')
        
        headlines = []
        seen_titles = set() # 중복 기사 제목을 걸러내기 위함

        for tag in headline_tags:
            title = tag.get_text().strip()
            if title and title not in seen_titles:
                headlines.append(title)
                seen_titles.add(title)
            
            # 최대 10개의 헤드라인만 가져옵니다.
            if len(headlines) >= 10:
                break
        
        if headlines:
            print("뉴스 검색 완료!")
        else:
            print("뉴스 헤드라인을 찾지 못했습니다. 웹페이지의 구조가 변경되었을 수 있습니다.")
            
        return headlines

    except requests.exceptions.RequestException as e:
        print(f"HTTP 요청 중 오류 발생: {e}")
        return None
    except Exception as e:
        print(f"뉴스 스크레이핑 중 오류 발생: {e}")
        return None

# --- 2단계: Gemini로 요약하는 함수 ---
def summarize_with_gemini(headlines, api_key):
    """Gemini Pro를 사용해 뉴스 헤드라인을 요약하는 함수"""
    print("Gemini Pro를 통해 뉴스를 요약합니다...")
    try:
        # Gemini API 키 설정
        genai.configure(api_key=api_key)
        
        # 사용할 모델 설정
        model = genai.GenerativeModel('gemini-1.5-flash') # 가볍고 빠른 모델

        # 헤드라인 목록을 하나의 문자열로 먼저 만듭니다.
        headline_text = "- " + "\n- ".join(headlines)

        # Gemini에게 보낼 프롬프트(명령어) 구성
        prompt = f"""
        다음은 최신 AI 뉴스 헤드라인 목록입니다. 
        이 헤드라인들을 바탕으로 오늘날 AI 분야의 주요 동향을 3~5문장의 친절한 어투로 요약해주세요.

        [뉴스 헤드라인]
        {headline_text}
        """

        # API 호출하여 요약 생성
        response = model.generate_content(prompt)
        
        print("요약 완료!")
        return response.text

    except Exception as e:
        print(f"Gemini 요약 중 오류 발생: {e}")
        return None

# --- 메인 실행 부분 ---
if __name__ == "__main__":
    load_dotenv() # 2. .env 파일의 변수를 환경변수로 로드!

    # 실행 시 검색어(query)를 인자로 받음
    parser = argparse.ArgumentParser(description="뉴스를 검색하고 Gemini로 요약합니다.")
    parser.add_argument('query', type=str, help='검색할 뉴스 키워드')
    args = parser.parse_args()

    # (중요!) 환경변수에서 API 키 가져오기
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("오류: GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("API 키를 설정하고 다시 시도해주세요.")
    else:
        # 1. 뉴스 스크레이핑 실행
        news_headlines = scrape_google_news(args.query)

        # 2. 스크레이핑 성공 시, 요약 실행
        if news_headlines:
            summary = summarize_with_gemini(news_headlines, GEMINI_API_KEY)
            if summary:
                print("\n✨ Gemini AI 뉴스 요약 ✨\n" + "="*30)
                print(summary)
        else:
            print("요약할 뉴스 헤드라인이 없습니다.")
