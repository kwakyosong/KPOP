# 필요한 라이브러리 및 모듈 임포트
import asyncio  # 비동기 작업을 지원하는 모듈
from playwright.async_api import async_playwright  # Playwright 비동기 API를 위한 모듈
import pandas as pd  # 데이터프레임 관리를 위한 모듈
from langdetect import detect, LangDetectException  # 텍스트 언어 감지를 위한 모듈
import time  # 시간 지연을 위한 모듈
import matplotlib.pyplot as plt  # 시각화를 위한 Matplotlib 라이브러리

# 유튜브 댓글 수집 및 처리 함수
async def scrape_youtube_comments(video_url, max_comments=500):
    """
    YouTube 동영상에서 댓글을 비동기로 수집하고 언어별로 분류하며 시각화하는 함수
    Args:
        video_url (str): 유튜브 비디오 URL
        max_comments (int): 수집할 최대 댓글 수 (기본값: 500)
    """
    async with async_playwright() as p:  # Playwright 실행 컨텍스트
        # Chromium 브라우저를 비동기로 실행
        browser = await p.chromium.launch(headless=False)
        
        # 새 페이지 생성
        page = await browser.new_page()
        
        # 유튜브 동영상 URL로 이동
        await page.goto(video_url)
        
        # 댓글 섹션 로드 대기 (최대 10초)
        await page.wait_for_selector("ytd-comments", timeout=10000)
        
        # 댓글 데이터를 저장할 리스트 초기화
        comments = []
        
        # 스크롤을 반복하여 댓글 로드 및 수집
        while len(comments) < max_comments:
            # 페이지 맨 아래로 스크롤
            await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
            time.sleep(1)  # 1초 대기
            
            # 약간 위로 스크롤하여 추가 댓글 로드 유도
            await page.evaluate("window.scrollBy(0, -1000)")
            time.sleep(1)  # 1초 대기
            
            # 다시 아래로 스크롤
            await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
            time.sleep(1)  # 1초 대기
            
            # 현재 페이지에서 댓글 요소 선택
            comment_elements = await page.query_selector_all("#content-text")
            
            # 수집된 댓글 중 새로운 댓글만 처리
            for comment in comment_elements[len(comments):]:
                # 댓글의 텍스트 가져오기
                comment_text = await comment.inner_text()
                # 댓글 리스트에 추가
                comments.append(comment_text)
                
                # 최대 댓글 수에 도달하면 종료
                if len(comments) >= max_comments:
                    break

            # 현재까지 수집된 댓글 수 출력
            print('comments length =', len(comments))

        # 브라우저 닫기
        await browser.close()
        
        # 댓글 데이터의 언어를 감지하고 분류
        comment_data = []
        for comment in comments:
            try:
                # 댓글 텍스트의 언어 감지
                lang = detect(comment)
            except LangDetectException:
                # 감지 실패 시 언어를 'unknown'으로 처리
                lang = "unknown"
            # 댓글과 언어 정보를 리스트에 추가
            comment_data.append({"Comment": comment, "Language": lang})
        
        # 데이터를 Pandas 데이터프레임으로 변환
        df = pd.DataFrame(comment_data)
        
        # 언어별로 그룹화하여 CSV 파일로 저장
        grouped = df.groupby("Language")
        for lang, group in grouped:
            # 각 언어에 해당하는 댓글 데이터를 CSV 파일로 저장
            group.to_csv(f"youtube_comments_{lang}.csv", index=False)
        
        print("댓글 수집 및 언어별 분류 완료")

        # 언어별 댓글 수를 시각화
        lang_counts = df['Language'].value_counts()  # 언어별 댓글 개수 계산
        plt.figure(figsize=(10, 6))  # 그래프 크기 설정
        lang_counts.plot(kind='bar')  # 막대그래프 생성
        plt.title("Number of Comments by Language")  # 그래프 제목
        plt.xlabel("Language")  # x축 레이블
        plt.ylabel("Number of Comments")  # y축 레이블
        plt.xticks(rotation=45)  # x축 레이블 회전
        plt.show()  # 그래프 표시

# 실행 코드: 유튜브 비디오 URL과 함께 함수 실행
video_url = "https://www.youtube.com/watch?v=DbXMjAYSa68"  # 유튜브 비디오 URL
asyncio.run(scrape_youtube_comments(video_url))  # 비동기 함수 실행
