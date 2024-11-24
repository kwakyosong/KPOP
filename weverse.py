# Playwright의 동기 API와 time 모듈 임포트
from playwright.sync_api import Playwright, sync_playwright
import time  # 대기 시간을 위해 사용

# Playwright 실행을 위한 함수 정의
def run(playwright: Playwright) -> None:
    # Chromium 브라우저를 실행 (headless=False로 GUI 브라우저 표시)
    browser = playwright.chromium.launch(headless=False)
    
    # 브라우저 컨텍스트 생성 (쿠키, 세션 분리 가능)
    context = browser.new_context()
    
    # 새 페이지 열기
    page = context.new_page()
    
    # Weverse 사이트로 이동
    page.goto("https://weverse.io/")
    
    # 'Sign in' 버튼 클릭
    page.get_by_role("button", name="Sign in").click()
    
    # 이메일 입력 필드 클릭
    page.get_by_placeholder("your@email.com").click()
    
    # 이메일 입력
    page.get_by_placeholder("your@email.com").fill("본인아이디")
    
    # 이메일 필드에서 Enter 키 입력 (다음 단계로 진행)
    page.get_by_placeholder("your@email.com").press("Enter")
    
    # 비밀번호 입력 필드 클릭
    page.get_by_placeholder("비밀번호").click()
    
    # 비밀번호 입력
    page.get_by_placeholder("비밀번호").fill("본인패스워드")
    
    # 비밀번호 필드에서 Enter 키 입력
    page.get_by_placeholder("비밀번호").press("Enter")
    
    # '로그인' 버튼 클릭
    page.get_by_role("button", name="로그인").click()

    # 이메일 인증코드 입력을 기다리며 사용자에게 안내 메시지 출력
    print("이메일 인증코드를 복사해 와서 수동으로 입력 후 엔터를 눌러주세요.")
    
    # 인증코드 입력 후 계속 진행하기 위해 사용자 입력 대기
    input("인증코드 입력 후 계속하려면 Enter를 누르세요...")

    # 인증코드 확인 버튼 클릭
    page.get_by_role("button", name="인증코드 확인").click()
    
    # 확인 버튼 클릭 (정확한 텍스트 매칭을 위해 `exact=True` 사용)
    page.get_by_role("button", name="확인", exact=True).click()

    # 종료 안내 메시지 출력
    print("5초 후 브라우저를 종료합니다...")
    
    # 5초 대기
    time.sleep(5)
    
    # 정상 종료 메시지 출력
    print("정상종료 ~~~")
    
    # 브라우저 컨텍스트 닫기 (열린 탭 및 세션 종료)
    context.close()
    
    # 브라우저 종료
    browser.close()

# Playwright 실행 (sync API로 실행)
with sync_playwright() as playwright:
    run(playwright)
