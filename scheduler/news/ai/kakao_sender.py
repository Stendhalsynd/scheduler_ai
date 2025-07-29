# kakao_sender.py

import requests
import json
import os

# 카카오 토큰을 저장할 파일
KAKAO_TOKEN_FILENAME = "kakao_token.json"

# API 키와 리프레시 토큰을 .env 파일에서 불러오기
REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY")
REFRESH_TOKEN = os.environ.get("KAKAO_REFRESH_TOKEN")

# 토큰 갱신 함수
def refresh_kakao_token():
    """리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다."""
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": REST_API_KEY,
        "refresh_token": REFRESH_TOKEN,
    }
    response = requests.post(url, data=data)
    result = response.json()
    
    if "access_token" in result:
        print("카카오 토큰이 성공적으로 갱신되었습니다.")
        # 새 액세스 토큰만 저장 (리프레시 토큰은 그대로 사용)
        tokens = {"access_token": result["access_token"]}
        with open(KAKAO_TOKEN_FILENAME, "w") as fp:
            json.dump(tokens, fp)
        return tokens["access_token"]
    else:
        print(f"카카오 토큰 갱신 실패: {result}")
        return None

# 나에게 메시지 보내기 함수
def send_kakao_message(text):
    """지정된 텍스트를 나에게 보내기 API를 통해 전송합니다."""
    try:
        # 저장된 토큰 읽기 시도
        with open(KAKAO_TOKEN_FILENAME, "r") as fp:
            tokens = json.load(fp)
        access_token = tokens["access_token"]
    except FileNotFoundError:
        # 파일이 없으면 토큰 갱신부터 시작
        access_token = refresh_kakao_token()
        if not access_token:
            return

    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {access_token}"}
    template_object = {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": "https://news.google.com/tbm=nws",
            "mobile_web_url": "https://news.google.com/tbm=nws"
        }
    }
    data = {"template_object": json.dumps(template_object)}
    
    response = requests.post(url, headers=headers, data=data)
    
    # 응답 코드가 200(성공)이 아니면 토큰 만료로 간주하고 갱신 후 재시도
    if response.status_code != 200:
        print(f"메시지 전송 실패({response.status_code}): {response.json()}")
        print("토큰을 갱신하고 재시도합니다.")
        new_access_token = refresh_kakao_token()
        if new_access_token:
            headers["Authorization"] = f"Bearer {new_access_token}"
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                print("메시지 재전송 성공!")
            else:
                print(f"메시지 재전송 실패: {response.json()}")
    else:
        print("카카오톡 메시지를 성공적으로 보냈습니다.")