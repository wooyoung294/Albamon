### [AI Challenge] QA

응모작으로 Cursor와 Playwright MCP를 이용해서 아래 4가지 항목에 대해서 자동화 테스트를 구현하고 수정하였습니다.

#### 주의사항 
#### .env파일에 꼭 값을 넣고 실행하시길 바랍니다.
LOGIN_ID  : 알바몬 아이디
LOGIN_PW  : 알바몬 패스워드
USER_NAME : 로그인한 유저 명

#### 실행결과 : 

1. 아이디 + 비밀번호 입력 로그인
2. 유효성 검증 (입력 값 누락 등)
3. 로그인 실패 시 오류 메시지 출력
4. 로그인 성공 시 마이페이지(/personal/mypage) 이동

#### curosr 폴더의 파일목록
tset_cursor: AI가 작성해준 원본 코드 파일
cursor.md  : 프롬프트 파일
mcp.json   : Playwright MCP 

#### modify 폴더의 파일목록
tset_modify: AI가 작성해준 코드를 수정한 파일
