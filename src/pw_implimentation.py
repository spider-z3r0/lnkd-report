#!usr/bin/env 

from time import sleep
from playwright.sync_api import sync_playwright
from .models import Account, Post
from datetime import datetime


def find_posts(accounts: list[Account]) -> list[Post]:
    posts: list[Post] = []

    with sync_playwright() as p:
        print("🚀 Launching browser...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("🔐 Navigating to LinkedIn login page...")
        page.goto("https://www.linkedin.com/login")
        input("✅ Press Enter when you're fully logged in and ready to continue...")

        for account in accounts:
            print(f"🔍 Visiting {account.name}")

            activity_url = str(account.linkedin_url).rstrip("/") + "/recent-activity/all/"
            page.goto(activity_url)
            sleep(5)

            post_elements = page.query_selector_all("div.feed-shared-update-v2")
            print(f"📦 Found {len(post_elements)} post containers for {account.name}")

            for post_el in post_elements:
                try:
                    post_id = post_el.get_attribute("data-urn") or "unknown-post-id"

                    # Expand "See more"
                    try:
                        see_more_btn = post_el.query_selector("button:has-text('...see more')")
                        if see_more_btn:
                            see_more_btn.click()
                            sleep(0.2)
                    except:
                        pass

                    content_el = post_el.query_selector("div.feed-shared-text__text-view")
                    content = content_el.text_content().strip() if content_el else "NO_CONTENT"

                    time_el = post_el.query_selector("time")
                    date_str = time_el.get_attribute("datetime") if time_el else None
                    post_date = (
                        datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        if date_str else datetime.utcnow()
                    )

                    hashtags = [word for word in content.split() if word.startswith("#")]
                    post_url = f"https://www.linkedin.com/feed/update/{post_id}"

                    post = Post(
                        post_id=post_id,
                        author=account.name,
                        date=post_date,
                        content=content,
                        post_url=post_url,
                        hashtags=hashtags,
                        source_account=account.name
                    )

                    posts.append(post)
                    print(f"✅ Added: {post_id}")

                except Exception as e:
                    print(f"⚠️ Error parsing post: {e}")

        browser.close()

    print(f"🎉 Scraping complete: {len(posts)} total posts captured")
    return posts

