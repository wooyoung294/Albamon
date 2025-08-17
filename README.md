#### [AI Challenge] QA — Cursor × Playwright MCP 자동화 테스트

Cursor와 Playwright MCP를 활용해 로그인 플로우를 자동화하고, Pytest/Allure 기반 리포트를 생성하도록 구성했습니다.
### 🚀 테스트 리포트 주소: https://albamon.wooyoung.site
 - SUITES: test_modify의 각 케이스에 tear_down을 누르신 후 browser_context에 테스트 영상이 포함되어 있습니다~
<img width="1896" height="934" alt="Image" src="https://github.com/user-attachments/assets/b78b2932-4eb2-4a4a-b016-f0294c4e932d" />

### 📁 프로젝트 구조(정리 버전)
```text
.
|-- cursor/                      # Cursor + MCP 관련 산출물
|   |-- test_cursor.py           # AI가 생성한 원본 테스트 코드
|   |-- cursor.md                # 프롬프트 문서
|   `-- mcp.json                 # Playwright MCP 설정
|
|-- modify/                      # 보완한 코드
|   `-- test_modify.py           # 수정/개선 버전
|
|-- .env                         # 환경변수 예시 파일(값은 비움)
`-- README.md                    # 본 문서
```

### 🔐 환경변수(.env)

.env 파일에 아래 값을 반드시 채운 뒤 실행하세요

LOGIN_ID=알바몬_아이디
LOGIN_PW=알바몬_패스워드
USER_NAME=로그인_유저_표시명

USER_NAME은 로그인 성공 후 마이페이지 또는 헤더 프로필 영역에서 노출되는 사용자명을 검증하는 데 사용합니다.

### ✅ 테스트 범위 (4가지)
1. 아이디 + 비밀번호 입력 로그인
2. 유효성 검증(입력 값 누락 등)
3. 로그인 실패 시 오류 메시지 노출 검증
4. 로그인 성공 후 마이페이지(/personal/mypage) 이동 확인
   
### 📋TC
| 대분류(페이지) | 중분류(UI영역) | 소분류(요소) | locator | pre-condition | 동작 | 기대결과 | 우선순위 |
|----------------|----------------|--------------|---------|---------------|------|----------|----------|
| 로그인 페이지 | 로그인 폼 | 아이디 입력 필드 | #memberId | 로그인 페이지 접속 | 아이디 입력 | 입력된 아이디가 표시됨 | P0 |
| 로그인 페이지 | 로그인 폼 | 비밀번호 입력 필드 | #memberPassword | 로그인 페이지 접속 | 비밀번호 입력 | 입력된 비밀번호가 마스킹되어 표시됨 | P0 |
| 로그인 페이지 | 로그인 폼 | 로그인 버튼 | button[type="submit"] | 아이디/비밀번호 입력 완료 | 로그인 버튼 클릭 | 로그인 성공 시 마이페이지로 이동 | P0 |
| 로그인 페이지 | 유효성 검증 | 아이디 누락 검증 | #memberId, #memberPassword | 로그인 페이지 접속 | 아이디만 입력하고 로그인 시도 | "비밀번호를 입력해 주세요." 알림 표시 | P1 |
| 로그인 페이지 | 유효성 검증 | 비밀번호 누락 검증 | #memberId, #memberPassword | 로그인 페이지 접속 | 비밀번호만 입력하고 로그인 시도 | "아이디를 입력해 주세요." 알림 표시 | P1 |
| 로그인 페이지 | 오류 처리 | 잘못된 계정 정보 | #memberId, #memberPassword | 로그인 페이지 접속 | 잘못된 계정 정보로 로그인 시도 | "아이디 또는 비밀번호가 일치하지 않습니다." 오류 메시지 표시 | P1 |
| 로그인 페이지 | 성공 처리 | 정상 로그인 | #memberId, #memberPassword, button[type="submit"] | 로그인 페이지 접속 | 올바른 계정 정보로 로그인 시도 | 마이페이지(/personal/mypage)로 이동, 사용자명 표시 | P0 |

### ✅ 결과물 검토 및 보완 설명
1. 처음에 AI가 Locator를 id값이 있음에도 불구하고 role로 가지고 와서 힘들었습니다.
2. 비정상적인 ID 와 PW 를 입력후 로그인 버튼을 클릭하면 /member/login 으로 요청후 응답값의 message로 alert를 표시해주었는데 AI의 경우 해당 로직을 작성해주지 않았습니다.
3. alert의 문자를 비교할때 contains를 사용해서 해당 문자열이 정확하게 원하는 값인지를 체크하지 않고 포함되어 있는지로 체크하고 있엇습니다.
4. alert에 대해서 리스너를 등록해주지 않았습니다. 
