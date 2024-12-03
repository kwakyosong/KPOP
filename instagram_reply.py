from playwright.sync_api import sync_playwright
import time

USERNAME = "사용자ID"  # Instagram 아이디
PASSWORD = "사용자PW"  # Instagram 비밀번호
URL = "https://www.instagram.com/reel/DBYcXyxvQW9/"  # 타겟 URL

def instagram_login(page):
    """Instagram 로그인 함수"""
    try:
        page.goto("https://www.instagram.com/accounts/login/")
        time.sleep(3)
        page.fill('input[name="username"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.click('button[type="submit"]')
        time.sleep(5)
        print("로그인 성공!")
        return True
    except Exception as e:
        print(f"로그인 실패: {str(e)}")
        return False

def scrape_comments(page):
    """Instagram 댓글 스크롤 및 수집"""
    scrollable_div_selector = 'div.x5yr21d.xw2csxc.x1odjw0f.x1n2onr6'
    comment_text_selector = 'span[dir="auto"]'
    page.wait_for_selector(scrollable_div_selector)
    comments_data = []
    for _ in range(30):  # 최대 30회 스크롤
        comments = page.query_selector_all(f'{scrollable_div_selector} {comment_text_selector}')
        for comment in comments:
            try:
                comment_text = comment.inner_text().strip()
                if comment_text and comment_text not in comments_data:
                    comments_data.append(comment_text)
                    print(f"댓글 수집: {comment_text}")
            except Exception as e:
                print(f"댓글 처리 중 오류: {e}")
        page.evaluate(
            f"""
            const div = document.querySelector('{scrollable_div_selector}');
            div.scrollBy(0, 500);
            """
        )
        time.sleep(2)  # 스크롤 후 로딩 대기
    print(f"\n총 수집된 댓글: {len(comments_data)}개")
    return comments_data

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        if instagram_login(page):
            page.goto(URL)
            time.sleep(5)  # 페이지 로딩 대기
            comments = scrape_comments(page)
            print("\n수집된 댓글 목록:")
            for comment in comments:
                print(comment)
        browser.close()

if __name__ == "__main__":
    main()
