import os

import allure
import pytest
import re
from playwright.sync_api import sync_playwright, expect
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()
# 추가
VIDEO_PATH = "videos/"
class TestAlbamonLogin:
    """알바몬 로그인 기능 테스트 클래스"""
    # Cursor 작성
    # @pytest.fixture(scope="class")
    # 수정
    @pytest.fixture(scope="function")
    def browser_context(self,request):
        """브라우저 컨텍스트 설정"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={"width": 1900, "height": 900},
                record_video_dir=VIDEO_PATH
            )
            page = context.new_page()
            yield page
            context.close()
            browser.close()
            with open(page.video.path(), "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"web_{request.node.name}_video",
                    attachment_type=allure.attachment_type.WEBM
                )

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
        # login_id = "dndud159"
        login_pw = os.getenv("LOGIN_PW")
        # login_pw = "emily5653!"

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

        self.page.wait_for_load_state("domcontentloaded")

        modal_header_btn = self.page.locator("#root-modal>div>section>header>button")
        expect(modal_header_btn).to_be_visible()
        modal_header_btn.click()
        expect(modal_header_btn).to_be_visible()
        modal_header_btn.click()

        # 사용자명이 표시되는지 확인
        expect(self.page.locator("text="+os.getenv('USER_NAME')+"님")).to_be_visible()

    def test_03_validation_id_missing(self):
        """TC03: 아이디 누락 시 유효성 검증 테스트"""
        # 비밀번호만 입력
        self.page.type("#memberPassword", "testpassword")


        # Cursor 작성
        # 로그인 버튼 클릭
        # self.page.click("button[type='submit']")

        # 알림 다이얼로그 확인
        # dialog = self.page.wait_for_event("dialog")
        # expect(dialog.message).to_contain("아이디를 입력해 주세요.")
        # dialog.accept()

        # 수정
        login_btn = self.page.locator('button[type="submit"]',has_text="로그인")

        dialog = None
        def handler(d):
            nonlocal dialog
            dialog = d
            dialog.accept()

        self.page.once("dialog", handler)
        login_btn.click()

        assert dialog.message == "아이디를 입력해 주세요."


    def test_04_validation_password_missing(self):
        """TC04: 비밀번호 누락 시 유효성 검증 테스트"""
        # 아이디만 입력
        self.page.fill("#memberId", "testuser")

        # 로그인 버튼 클릭
        # self.page.click("button[type='submit']")

        # 알림 다이얼로그 확인
        # dialog = self.page.wait_for_event("dialog")
        # expect(dialog.message).to_contain("비밀번호를 입력해 주세요.")
        # dialog.accept()

        # 수정
        login_btn = self.page.locator('button[type="submit"]',has_text="로그인")

        dialog = None
        def handler(d):
            nonlocal dialog
            dialog = d
            dialog.accept()

        self.page.once("dialog", handler)
        login_btn.click()

        assert dialog.message == "비밀번호를 입력해 주세요."

    def test_05_validation_invalid_credentials(self):
        """TC05: 잘못된 계정 정보로 로그인 시도 시 오류 메시지 테스트"""
        # 잘못된 계정 정보 입력
        self.page.type("#memberId", "invaliduser")
        self.page.type("#memberPassword", "invalidpassword")
        # 로그인 버튼 클릭
        # self.page.click("button[type='submit']")

        # 알림 다이얼로그 확인
        # dialog = self.page.wait_for_event("dialog")
        # expect(dialog.message).to_contain("아이디 또는 비밀번호가 일치하지 않습니다.")
        # dialog.accept()

        # 수정
        login_btn = self.page.get_by_role("button", name="로그인", exact=True)

        with (self.page.expect_response(
                lambda r: r.request.method == "POST" and re.search(r"/member/login", r.url)
        ) as resp_info,
            self.page.expect_event("dialog", timeout=5000) as dlg_info):

            login_btn.click(no_wait_after=True)

        # 응답 검증
        resp = resp_info.value
        assert resp.status == 400

        # 다이얼로그 검증
        dialog = dlg_info.value
        dialog.accept()
        assert dialog.message == resp.json()["message"]

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
import os

import allure
import pytest
import re
from playwright.sync_api import sync_playwright, expect
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()
# 추가
VIDEO_PATH = "videos/"
class TestAlbamonLogin:
    """알바몬 로그인 기능 테스트 클래스"""
    # Cursor 작성
    # @pytest.fixture(scope="class")
    # 수정
    @pytest.fixture(scope="function")
    def browser_context(self,request):
        """브라우저 컨텍스트 설정"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={"width": 1900, "height": 900},
                record_video_dir=VIDEO_PATH
            )
            page = context.new_page()
            yield page
            context.close()
            browser.close()
            with open(page.video.path(), "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"web_{request.node.name}_video",
                    attachment_type=allure.attachment_type.WEBM
                )

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
        # login_id = "dndud159"
        login_pw = os.getenv("LOGIN_PW")
        # login_pw = "emily5653!"

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

        self.page.wait_for_load_state("domcontentloaded")

        modal_header_btn = self.page.locator("#root-modal>div>section>header>button")
        expect(modal_header_btn).to_be_visible()
        modal_header_btn.click()
        expect(modal_header_btn).to_be_visible()
        modal_header_btn.click()

        # 사용자명이 표시되는지 확인
        expect(self.page.locator("text="+os.getenv('USER_NAME')+"님")).to_be_visible()

    def test_03_validation_id_missing(self):
        """TC03: 아이디 누락 시 유효성 검증 테스트"""
        # 비밀번호만 입력
        self.page.type("#memberPassword", "testpassword")


        # Cursor 작성
        # 로그인 버튼 클릭
        # self.page.click("button[type='submit']")

        # 알림 다이얼로그 확인
        # dialog = self.page.wait_for_event("dialog")
        # expect(dialog.message).to_contain("아이디를 입력해 주세요.")
        # dialog.accept()

        # 수정
        login_btn = self.page.locator('button[type="submit"]',has_text="로그인")

        dialog = None
        def handler(d):
            nonlocal dialog
            dialog = d
            dialog.accept()

        self.page.once("dialog", handler)
        login_btn.click()

        assert dialog.message == "아이디를 입력해 주세요."


    def test_04_validation_password_missing(self):
        """TC04: 비밀번호 누락 시 유효성 검증 테스트"""
        # 아이디만 입력
        self.page.fill("#memberId", "testuser")

        # 로그인 버튼 클릭
        # self.page.click("button[type='submit']")

        # 알림 다이얼로그 확인
        # dialog = self.page.wait_for_event("dialog")
        # expect(dialog.message).to_contain("비밀번호를 입력해 주세요.")
        # dialog.accept()

        # 수정
        login_btn = self.page.locator('button[type="submit"]',has_text="로그인")

        dialog = None
        def handler(d):
            nonlocal dialog
            dialog = d
            dialog.accept()

        self.page.once("dialog", handler)
        login_btn.click()

        assert dialog.message == "비밀번호를 입력해 주세요."

    def test_05_validation_invalid_credentials(self):
        """TC05: 잘못된 계정 정보로 로그인 시도 시 오류 메시지 테스트"""
        # 잘못된 계정 정보 입력
        self.page.type("#memberId", "invaliduser")
        self.page.type("#memberPassword", "invalidpassword")
        # 로그인 버튼 클릭
        # self.page.click("button[type='submit']")

        # 알림 다이얼로그 확인
        # dialog = self.page.wait_for_event("dialog")
        # expect(dialog.message).to_contain("아이디 또는 비밀번호가 일치하지 않습니다.")
        # dialog.accept()

        # 수정
        login_btn = self.page.get_by_role("button", name="로그인", exact=True)

        with self.page.expect_response(
                lambda r: r.request.method == "POST" and re.search(r"/member/login(?:\?|$)", r.url)
        ) as resp_info, \
                self.page.expect_event("dialog", timeout=5000) as dlg_info:

            login_btn.click(no_wait_after=True)

        # 응답 검증
        resp = resp_info.value
        assert resp.status == 400

        # 다이얼로그 검증
        dialog = dlg_info.value
        dialog.accept()
        assert dialog.message == resp.json()["message"]

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
