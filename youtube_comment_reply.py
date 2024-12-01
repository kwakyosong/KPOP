from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# Selenium WebDriver 설정
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)

# 브라우저 위치를 화면 오른쪽으로 이동
driver.set_window_position(1000, 0)  # x=1000, y=0 위치로 설정 (조정 가능)
driver.set_window_size(800, 800)  # 브라우저 창 크기 설정

# YouTube URL 설정
url = "https://www.youtube.com/watch?v=sWXGbkM0tBI"
driver.get(url)

# 페이지 로딩 대기
time.sleep(3)

def scroll_to_comments_section(driver):
    """댓글 섹션이 나타날 때까지 스크롤 이동"""
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)
        try:
            # 댓글 섹션 로드 확인
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-comments#comments")))
            print("<ytd-comments> 섹션 로드 완료!")
            break
        except Exception:
            # 스크롤 끝에 도달했는지 확인
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                print("댓글 섹션을 찾을 수 없습니다.")
                break
            last_height = new_height

def collect_comments_and_replies(driver, max_scrolls=50, max_no_change_count=10):
    """댓글 및 답글 수집 (스크롤 포함, 추가 종료 조건 적용)"""
    collected_comments = set()  # 중복 방지용
    total_replies = 0  # 답글 숫자 총합
    scroll_count = 0  # 현재 스크롤 횟수
    no_change_count = 0  # 댓글 수 변화 없는 횟수
    previous_total_posts = 0  # 이전 전체 글 개수

    while scroll_count < max_scrolls and no_change_count < max_no_change_count:
        # 댓글 섹션에서 댓글을 찾기
        comment_threads = driver.find_elements(By.CSS_SELECTOR, "ytd-comment-thread-renderer")
        for thread_index, thread in enumerate(comment_threads, 1):  # thread_index 추가
            try:
                # 댓글 수집
                comment_element = thread.find_element(By.CSS_SELECTOR, "yt-attributed-string#content-text")
                comment_text = comment_element.text
                if comment_text not in collected_comments:
                    collected_comments.add(comment_text)
                    print(f"댓글 {len(collected_comments)}: {comment_text}")
                    # 댓글이 성공적으로 수집된 경우에만 답글 처리
                    try:
                        reply_button = thread.find_element(By.CSS_SELECTOR, "yt-button-shape button")
                        aria_label = reply_button.get_attribute("aria-label")
                        if aria_label and re.search(r"\d", aria_label):  # 숫자가 포함된 aria-label
                            match = re.search(r"(\d+)", aria_label)
                            if match:
                                replies_count = int(match.group(1))
                                total_replies += replies_count
                                print(f"  답글 버튼: {aria_label} (답글 {replies_count}개 추가)")
                            reply_button.click()
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#replies yt-attributed-string#content-text")))
                            replies = driver.find_elements(By.CSS_SELECTOR, "div#replies yt-attributed-string#content-text")
                            for reply in replies:
                                print(f"    답글 {reply.text}")
                    except Exception:
                        print("  답글 버튼 없음 -- 무시")
                        continue
            except Exception:
                continue
        # 스크롤 아래로 이동
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(2)  # DOM 업데이트 대기
        # 현재 상태 출력
        total_comments = len(collected_comments)
        total_posts = total_comments + total_replies
        print(f"--------------------------------- {scroll_count + 1}번째 Loop: 댓글 {total_comments}개, 답글 {total_replies}개, 전체 글 {total_posts}개")
        # 종료 조건 체크
        if total_posts == previous_total_posts:
            no_change_count += 1
        else:
            no_change_count = 0
            previous_total_posts = total_posts
        scroll_count += 1

    print(f"수집 종료: 스크롤 {scroll_count}번, 댓글 {len(collected_comments)}개, 답글 {total_replies}개, 전체 글 {total_posts}개")
    total_comments = len(collected_comments)
    total_posts = total_comments + total_replies
    print(f"총 댓글: {total_comments}개, 답글: {total_replies}개, 전체 글: {total_posts}개")
    print(f"최대 스크롤 {max_scrolls}번 도달, 수집 종료.")

# 댓글 섹션으로 스크롤 이동
scroll_to_comments_section(driver)

# 댓글 및 답글 수집
collect_comments_and_replies(driver, 2000)

# 브라우저 닫기
driver.quit()
