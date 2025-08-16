import os
import pytest
import re
from playwright.sync_api import sync_playwright, expect
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

class TestAlbamonLogin:
    """알바몬 로그인 기능 테스트 클래스"""

    @pytest.fixture(scope="class")
    def browser_context(self):
        """브라우저 컨텍스트 설정"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=1000)
            context = browser.new_context()
            page = context.new_page()
            yield page
            context.close()
            browser.close()

    @pytest.fixture(autouse=True)
    def setup_teardown(self, browser_context):
        """각 테스트 전후 설정/정리"""
        self.page = browser_context
        # 각 테스트 전에 로그인 페이지로 이동
        self.page.goto("https://m.albamon.com/user-account/login?my_page=1&memberType=PERSONAL")
        yield
        # 각 테스트 후 로그아웃 (로그인된 상태라면)
        try:
            if "/personal/mypage" in self.page.url:
                self.page.click("text=회원정보")
                self.page.click("text=로그아웃")
        except:
            pass

    def test_01_login_form_elements_exist(self):
        """TC01: 로그인 폼 요소들이 존재하는지 확인"""
        # 아이디 입력 필드 확인
        expect(self.page.locator("#memberId")).to_be_visible()
        expect(self.page.locator("#memberId")).to_have_attribute("placeholder", "아이디")

        # 비밀번호 입력 필드 확인
        expect(self.page.locator("#memberPassword")).to_be_visible()
        expect(self.page.locator("#memberPassword")).to_have_attribute("placeholder", "비밀번호")

        # 로그인 버튼 확인
        expect(self.page.locator("button[type='submit']")).to_be_visible()
        expect(self.page.locator("button[type='submit']")).to_contain_text("로그인")

    def test_02_successful_login(self):
        """TC02: 정상적인 로그인 성공 테스트"""
        # 환경변수에서 계정 정보 가져오기
        login_id = os.getenv("LOGIN_ID")
        login_pw = os.getenv("LOGIN_PW")

        assert login_id, "LOGIN_ID 환경변수가 설정되지 않았습니다."
        assert login_pw, "LOGIN_PW 환경변수가 설정되지 않았습니다."

        # 아이디 입력
        self.page.fill("#memberId", login_id)

        # 비밀번호 입력
        self.page.fill("#memberPassword", login_pw)

        # 로그인 버튼 클릭
        self.page.click("button[type='submit']")

        # 마이페이지로 이동 확인 (URL 패턴 매칭)
        expect(self.page).to_have_url(re.compile(r".*/personal/mypage.*"))

        # 사용자명이 표시되는지 확인
        expect(self.page.locator("text=님")).to_be_visible()

    def test_03_validation_id_missing(self):
        """TC03: 아이디 누락 시 유효성 검증 테스트"""
        # 비밀번호만 입력
        self.page.fill("#memberPassword", "testpassword")

        # 로그인 버튼 클릭
        self.page.click("button[type='submit']")

        # 알림 다이얼로그 확인
        dialog = self.page.wait_for_event("dialog")
        expect(dialog.message).to_contain("아이디를 입력해 주세요.")
        dialog.accept()

    def test_04_validation_password_missing(self):
        """TC04: 비밀번호 누락 시 유효성 검증 테스트"""
        # 아이디만 입력
        self.page.fill("#memberId", "testuser")

        # 로그인 버튼 클릭
        self.page.click("button[type='submit']")

        # 알림 다이얼로그 확인
        dialog = self.page.wait_for_event("dialog")
        expect(dialog.message).to_contain("비밀번호를 입력해 주세요.")
        dialog.accept()

    def test_05_validation_invalid_credentials(self):
        """TC05: 잘못된 계정 정보로 로그인 시도 시 오류 메시지 테스트"""
        # 잘못된 계정 정보 입력
        self.page.fill("#memberId", "invaliduser")
        self.page.fill("#memberPassword", "invalidpassword")

        # 로그인 버튼 클릭
        self.page.click("button[type='submit']")

        # 알림 다이얼로그 확인
        dialog = self.page.wait_for_event("dialog")
        expect(dialog.message).to_contain("아이디 또는 비밀번호가 일치하지 않습니다.")
        dialog.accept()

    def test_06_login_state_persistence(self):
        """TC06: 로그인 상태 유지 체크박스 동작 테스트"""
        # 로그인 상태 유지 체크박스 확인
        checkbox = self.page.locator("input[type='checkbox']")
        expect(checkbox).to_be_checked()

        # 체크박스 해제
        checkbox.uncheck()
        expect(checkbox).not_to_be_checked()

        # 체크박스 다시 체크
        checkbox.check()
        expect(checkbox).to_be_checked()

    def test_07_social_login_buttons_exist(self):
        """TC07: 소셜 로그인 버튼들이 존재하는지 확인"""
        # 네이버 로그인 버튼
        expect(self.page.locator("text=네이버 계정으로 로그인")).to_be_visible()

        # 카카오톡 로그인 버튼
        expect(self.page.locator("text=카카오톡 계정으로 로그인")).to_be_visible()

        # 페이스북 로그인 버튼
        expect(self.page.locator("text=페이스북 계정으로 로그인")).to_be_visible()

        # 구글 로그인 버튼
        expect(self.page.locator("text=구글 계정으로 로그인")).to_be_visible()

        # 애플 로그인 버튼
        expect(self.page.locator("text=애플 계정으로 로그인")).to_be_visible()

    def test_08_utility_links_exist(self):
        """TC08: 유틸리티 링크들이 존재하는지 확인"""
        # 아이디 찾기 링크
        expect(self.page.locator("text=아이디 찾기")).to_be_visible()

        # 비밀번호 찾기 링크
        expect(self.page.locator("text=비밀번호 찾기")).to_be_visible()

        # 회원가입 링크
        expect(self.page.locator("text=회원가입")).to_be_visible()

    def test_09_member_type_tabs_exist(self):
        """TC09: 회원 유형 탭들이 존재하는지 확인"""
        # 개인회원 탭
        expect(self.page.locator("text=개인회원")).to_be_visible()

        # 기업회원 탭
        expect(self.page.locator("text=기업회원")).to_be_visible()

    def test_10_page_title_and_header(self):
        """TC10: 페이지 제목과 헤더 확인"""
        # 페이지 제목 확인
        expect(self.page).to_have_title("알바몬·잡코리아 통합 로그인")

        # 헤더 텍스트 확인
        expect(self.page.locator("text=알바몬·잡코리아 통합 로그인")).to_be_visible()


if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v", "-s"])
