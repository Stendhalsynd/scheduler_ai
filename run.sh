#!/bin/bash

# .env 파일의 환경변수를 로드합니다.
source .env

# curl 명령어 실행 시 로드된 환경변수($GEMINI_API_KEY)를 사용합니다.
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent" \
  -H 'Content-Type: application/json' \
  -H "X-goog-api-key: $GEMINI_API_KEY" \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'