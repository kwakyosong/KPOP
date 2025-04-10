import asyncio
from playwright.async_api import async_playwright

async def scrape_youtube_shorts():
    url = "https://www.youtube.com/hashtag/%EA%B3%A0%EC%9E%89%EC%84%B8%EB%B8%90%ED%8B%B4/shorts"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)

        await page.wait_for_selector("div#contents")

        prev_count = 0
        same_count_repeat = 0

        while True:
            # 현재 항목 수집 및 출력
            items = await page.query_selector_all("ytd-rich-item-renderer")
            current_count = len(items)

            print(f"\n[스크롤 전] 현재 항목 수: {current_count}")
            for item in items[prev_count:]:  # 이전에 출력한 건 건너뜀
                try:
                    title_el = await item.query_selector("h3.shortsLockupViewModelHostMetadataTitle")
                    views_el = await item.query_selector("div[aria-label*='조회수']")

                    title = await title_el.get_attribute("aria-label") if title_el else "제목 없음"
                    views = await views_el.get_attribute("aria-label") if views_el else "조회수 없음"

                    print(f"[제목] {title}")
                    print(f"[조회수] {views}")
                    print("-" * 50)
                except:
                    continue

            if current_count == prev_count:
                same_count_repeat += 1
                if same_count_repeat >= 3:
                    print("✅ 스크롤 완료: 더 이상 항목 없음")
                    break
            else:
                same_count_repeat = 0

            prev_count = current_count

            print("⏳ 3초 대기 후 스크롤 진행...\n")
            await asyncio.sleep(3)
            await page.mouse.wheel(0, 10000)

        print(f"\n🎉 전체 수집된 Shorts 영상 개수: {len(items)} 개")
        await browser.close()

# 실행
asyncio.run(scrape_youtube_shorts())
