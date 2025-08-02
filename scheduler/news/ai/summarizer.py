import requests
from bs4 import BeautifulSoup
import urllib.parse
import argparse
import re
import os
import google.generativeai as genai
from dotenv import load_dotenv # 1. 라이브러리 불러오기
from kakao_sender import send_kakao_message # kakao_sender 임포트
from datetime import datetime

# [추가] 이전에 보낸 헤드라인을 기록할 파일
HISTORY_FILE = "sent_headlines.txt"

# [추가] 이전에 보낸 헤드라인을 불러오는 함수
def load_sent_headlines():
    """기록 파일에서 이전에 보낸 헤드라인을 불러옵니다."""
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()
    
# [추가] 새로 보낸 헤드라인을 기록 파일에 추가하는 함수
def add_headlines_to_history(headlines):
    """새로 처리한 헤드라인을 기록 파일에 추가합니다."""
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        for headline in headlines:
            f.write(headline + '\n')

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

# --- 2단계: Gemini로 요약하는 함수 ([수정] 프롬프트 변경) ---
def summarize_with_gemini(headlines, api_key):
    """Gemini Pro를 사용해 각 뉴스 헤드라인을 개별적으로 요약합니다."""
    print("Gemini Pro를 통해 뉴스를 요약합니다...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # [수정] 프롬프트를 각 헤드라인별 요약 및 목록 형식으로 요청하도록 변경
        prompt = f"""
        당신은 뉴스 요약 전문가입니다. 다음 각 뉴스 헤드라인에 대해, 핵심 내용을 2~3문장으로 요약해주세요.
        결과는 아래와 같이 각 항목을 구분하여 목록 형태로 보여주세요.

        [뉴스 헤드라인 목록]
        - {"\n- ".join(headlines)}

        [출력 형식 예시]
        - [뉴스 제목]: 뉴스 요약 내용입니다.
        - [다른 뉴스 제목]: 다른 뉴스에 대한 요약입니다.
        """

        response = model.generate_content(prompt)
        print("요약 완료!")
        return response.text.strip()

    except Exception as e:
        print(f"Gemini 요약 중 오류 발생: {e}")
        return None


# --- 메인 실행 부분 ([수정] 중복 제거 로직 추가) ---
if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description="새로운 뉴스를 검색, 요약하고 카카오톡으로 전송합니다.")
    parser.add_argument('query', type=str, help='검색할 뉴스 키워드')
    args = parser.parse_args()

    if not os.environ.get("GEMINI_API_KEY") or not os.environ.get("KAKAO_REST_API_KEY"):
        print("오류: API 키가 설정되지 않았습니다.")
    else:
        # [수정] 1. 이전에 보낸 헤드라인 불러오기
        sent_headlines = load_sent_headlines()
        print(f"기존에 전송한 뉴스 {len(sent_headlines)}건을 불러왔습니다.")

        # [수정] 2. 새로운 뉴스 스크레이핑
        all_headlines = scrape_google_news(args.query)

        if all_headlines:
            # [수정] 3. 새로운 헤드라인만 필터링
            new_headlines = [h for h in all_headlines if h not in sent_headlines]
            
            if not new_headlines:
                print("새로운 뉴스가 없습니다. 프로그램을 종료합니다.")
            else:
                print(f"새로운 뉴스 {len(new_headlines)}건을 발견했습니다.")
                # [수정] 4. 새로운 뉴스만 요약
                summary = summarize_with_gemini(new_headlines, os.environ.get("GEMINI_API_KEY"))
                
                if summary:
                    # 터미널에도 출력
                    print("\n✨ Gemini AI 뉴스 요약 ✨\n" + "="*30)
                    print(summary)
                    
                    # [수정] 5. 카톡 메시지 생성 및 발송
                    today_str = datetime.now().strftime('%Y년 %m월 %d일')
                    message = f"📰 {today_str} - '{args.query}' 신규 뉴스\n\n{summary}"
                    send_kakao_message(message)
                    
                    # [수정] 6. 성공적으로 보낸 후, 새 헤드라인을 기록
                    add_headlines_to_history(new_headlines)
                    print("새로운 뉴스 목록을 히스토리에 추가했습니다.")
        else:
            print("요약할 뉴스 헤드라인이 없습니다.")