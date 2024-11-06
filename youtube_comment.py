import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from langdetect import detect, LangDetectException
import time
import matplotlib.pyplot as plt

async def scrape_youtube_comments(video_url, max_comments=500):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 유튜브 비디오 URL로 이동
        await page.goto(video_url)
        
        # 댓글 섹션이 로드될 때까지 대기
        await page.wait_for_selector("ytd-comments", timeout=10000)
        
        # 댓글 수집을 위한 초기화
        comments = []
        
        # 스크롤을 통해 댓글을 로드하면서 수집
        while len(comments) < max_comments:
            # 스크롤을 아래로 내린 후 대기
            await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
            time.sleep(1)  # 1초 대기
            
            # 스크롤을 다시 위로 올려서 댓글 로딩을 유도
            await page.evaluate("window.scrollBy(0, -1000)")
            time.sleep(1)  # 1초 대기
            
            await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
            time.sleep(1)  # 1초 대기
            
            # 현재 페이지의 댓글 요소 가져오기
            comment_elements = await page.query_selector_all("#content-text")
            
            for comment in comment_elements[len(comments):]:
                comment_text = await comment.inner_text()
                comments.append(comment_text)
                
                if len(comments) >= max_comments:
                    break

            # 댓글 수 확인 출력
            print('comments length =', len(comments))

        await browser.close()
        
        # 수집한 댓글을 언어별로 분류하여 저장
        comment_data = []
        for comment in comments:
            try:
                lang = detect(comment)
            except LangDetectException:
                lang = "unknown"
            comment_data.append({"Comment": comment, "Language": lang})
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(comment_data)
        
        # 언어별로 그룹화하여 저장
        grouped = df.groupby("Language")
        for lang, group in grouped:
            group.to_csv(f"youtube_comments_{lang}.csv", index=False)
        
        print("댓글 수집 및 언어별 분류 완료")

        # 언어별 댓글 수 시각화
        lang_counts = df['Language'].value_counts()
        plt.figure(figsize=(10, 6))
        lang_counts.plot(kind='bar')
        plt.title("Number of Comments by Language")
        plt.xlabel("Language")
        plt.ylabel("Number of Comments")
        plt.xticks(rotation=45)
        plt.show()

# 실행 코드
video_url = "https://www.youtube.com/watch?v=DbXMjAYSa68"
asyncio.run(scrape_youtube_comments(video_url))
