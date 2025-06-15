#!usr/bin/env 

from time import sleep
from datetime import datetime
from playwright.sync_api import sync_playwright
from .models import Account, Post

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

                    # Check for repost
                    header = post_el.query_selector("span.update-components-header__text-view")
                    is_repost = header and "reposted this" in header.text_content().lower()
                    original_author = None
                    if is_repost:
                        orig_author_el = post_el.query_selector("a.update-components-actor__meta-link span span[aria-hidden='true']")
                        if orig_author_el:
                            original_author = orig_author_el.text_content().strip()
                    else:
                        is_repost = False
                        original_author = None


                    # Expand "see more"
                    try:
                        see_more_btn = post_el.query_selector("button.feed-shared-inline-show-more-text__see-more-less-toggle")
                        if see_more_btn:
                            see_more_btn.click()
                            sleep(0.2)
                    except Exception:
                        pass

                    # Pull content from span[dir='ltr'] inside update-components-text
                    text_block = post_el.query_selector("div.update-components-text")
                    if text_block:
                        spans = text_block.query_selector_all("span.break-words span[dir='ltr']")
                        content = " ".join([s.text_content().strip() for s in spans]) if spans else "NO_CONTENT"
                    else:
                        content = "NO_CONTENT"

                    # Post date
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
                        source_account=account.name,
                        is_repost=is_repost,
                        original_author=original_author
                    )

                    posts.append(post)
                    print(f"✅ Added post: {post_id} {'(repost)' if is_repost else ''}")

                except Exception as e:
                    print(f"⚠️ Error parsing post: {e}")

        browser.close()

    print(f"🎉 Done. Captured {len(posts)} posts total.")
    return posts

