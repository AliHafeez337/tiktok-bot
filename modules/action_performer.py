from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from .utils import safe_find_element, safe_find_clickable, safe_click, dismiss_popups, random_delay, setup_logging
import random
import time

logger = setup_logging()


def _wait_for_video_page(driver, timeout=15):
    """Wait until a TikTok video page has loaded."""
    page_selectors = [
        '[data-e2e="browse-video-desc"]',
        'button[data-e2e="like-icon"]',
        '[data-e2e="like-icon"]',
        '[data-e2e="comment-count"]',
    ]
    for selector in page_selectors:
        if safe_find_element(driver, By.CSS_SELECTOR, selector, timeout=timeout):
            return True
    return False


def _ensure_comments_panel(driver):
    """Open the comments panel and select the Comments tab if needed."""
    icon_selectors = [
        'span[data-e2e="comment-icon"]',
        'button[data-e2e="comment-icon"]',
        '[data-e2e="comment-icon"]',
    ]
    for selector in icon_selectors:
        icon = safe_find_clickable(driver, By.CSS_SELECTOR, selector, timeout=3)
        if icon:
            safe_click(driver, icon)
            random_delay(1, 2)
            break

    tab_selectors = [
        (By.XPATH, "//*[self::p or self::span or self::div][normalize-space()='Comments']"),
        (By.XPATH, "//button[contains(., 'Comments')]"),
        (By.XPATH, "//*[@role='tab' and contains(., 'Comments')]"),
        (By.CSS_SELECTOR, '[data-e2e="comment-tab"]'),
        (By.CSS_SELECTOR, '[data-e2e="browse-comment-tab"]'),
    ]
    for by, value in tab_selectors:
        tab = safe_find_clickable(driver, by, value, timeout=3)
        if tab:
            safe_click(driver, tab)
            random_delay(0.5, 1)
            logger.info("Selected Comments tab")
            return True

    return False


def _find_comment_editor(driver):
    """Find the inner Draft.js comment editor (not the outer container)."""
    editor_selectors = [
        (By.CSS_SELECTOR, 'div[data-e2e="comment-input"] div[contenteditable="true"]'),
        (By.CSS_SELECTOR, 'div[data-e2e="comment-text"] div[contenteditable="true"]'),
        (By.CSS_SELECTOR, 'div[data-e2e="comment-input"] [role="textbox"]'),
        (By.CSS_SELECTOR, '.public-DraftEditor-content[contenteditable="true"]'),
        (By.CSS_SELECTOR, '[class*="InputEditorContainer"] div[contenteditable="true"]'),
        (By.XPATH, "//div[@data-e2e='comment-input']//div[@contenteditable='true']"),
    ]

    for by, value in editor_selectors:
        for element in driver.find_elements(by, value):
            try:
                if element.is_displayed():
                    return element
            except Exception:
                continue

    return safe_find_element(
        driver,
        By.CSS_SELECTOR,
        'div[data-e2e="comment-input"] div[contenteditable="true"]',
        timeout=8,
    )


def _type_in_comment_editor(driver, editor, comment_text):
    """Type into TikTok's Draft.js comment field."""
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
        editor,
    )
    random_delay(0.3, 0.6)

    if not safe_click(driver, editor):
        driver.execute_script("arguments[0].focus();", editor)

    random_delay(0.3, 0.6)

    try:
        editor.send_keys(comment_text)
        return True
    except Exception:
        pass

    try:
        ActionChains(driver).click(editor).pause(0.2).send_keys(comment_text).perform()
        return True
    except Exception:
        pass

    try:
        driver.execute_script(
            """
            const el = arguments[0];
            el.focus();
            el.textContent = arguments[1];
            el.dispatchEvent(new InputEvent('input', { bubbles: true }));
            """,
            editor,
            comment_text,
        )
        return True
    except Exception:
        return False


def get_latest_posts(driver, username, count=3):
    """Get latest posts of a user."""
    try:
        logger.info(f"Getting latest posts for @{username}")
        driver.get(f"https://www.tiktok.com/@{username}")
        random_delay(2, 3)
        dismiss_popups(driver)

        safe_find_element(
            driver,
            By.CSS_SELECTOR,
            'div[data-e2e="user-post-item"], a[href*="/video/"]',
            timeout=10,
        )
        time.sleep(1)

        post_links = []
        selectors = [
            'div[data-e2e="user-post-item"] a[href*="/video/"]',
            'a[href*="/video/"]',
        ]
        for selector in selectors:
            for element in driver.find_elements(By.CSS_SELECTOR, selector):
                href = element.get_attribute('href')
                if href and '/video/' in href and href not in post_links:
                    post_links.append(href)
                if len(post_links) >= count:
                    break
            if post_links:
                break

        logger.info(f"Found {len(post_links)} posts for @{username}")
        return post_links[:count]

    except Exception as e:
        logger.error(f"Error getting posts: {e}")
        return []


def comment_on_post(driver, post_url, comment_text):
    """Comment on a post."""
    try:
        logger.info(f"Commenting on post: {post_url}")
        driver.get(post_url)
        random_delay(2, 3)
        dismiss_popups(driver)

        if not _wait_for_video_page(driver):
            logger.warning("Video page did not finish loading")
            return False

        _ensure_comments_panel(driver)
        random_delay(1, 2)

        comment_input = _find_comment_editor(driver)
        if not comment_input:
            logger.info("Comment editor not visible yet, retrying after opening Comments tab")
            _ensure_comments_panel(driver)
            random_delay(1, 2)
            comment_input = _find_comment_editor(driver)

        if not comment_input:
            logger.warning("Could not find comment input")
            return False

        if not _type_in_comment_editor(driver, comment_input, comment_text):
            logger.warning("Could not type into comment input")
            return False

        random_delay(0.5, 1)

        post_selectors = [
            (By.CSS_SELECTOR, 'button[data-e2e="comment-post"]'),
            (By.CSS_SELECTOR, 'div[data-e2e="comment-post"]'),
            (By.XPATH, "//button[contains(@data-e2e, 'comment-post')]"),
            (By.XPATH, "//div[contains(@data-e2e, 'comment-post')]"),
            (By.XPATH, "//button[contains(., 'Post')]"),
        ]

        post_button = None
        for by, value in post_selectors:
            post_button = safe_find_clickable(driver, by, value, timeout=5)
            if post_button:
                break

        if post_button and safe_click(driver, post_button):
            random_delay(1, 2)
            logger.info(f"Comment posted: '{comment_text}'")
            return True

        try:
            comment_input.send_keys(Keys.ENTER)
            random_delay(1, 2)
            logger.info(f"Comment posted via Enter key: '{comment_text}'")
            return True
        except Exception:
            pass

        logger.warning("Could not find or click post button")
        return False

    except Exception as e:
        logger.error(f"Error commenting: {e}")
        return False


def like_post(driver, post_url):
    """Like a post."""
    try:
        logger.info(f"Liking post: {post_url}")
        driver.get(post_url)
        random_delay(2, 3)
        dismiss_popups(driver)

        like_selectors = [
            (By.CSS_SELECTOR, 'button[data-e2e="like-icon"]'),
            (By.CSS_SELECTOR, 'button[data-e2e="browse-like-icon"]'),
            (By.CSS_SELECTOR, '[data-e2e="like-icon"]'),
            (By.XPATH, "//button[contains(@aria-label, 'Like')]"),
        ]

        like_button = None
        for by, value in like_selectors:
            like_button = safe_find_clickable(driver, by, value, timeout=8)
            if like_button:
                break

        if not like_button:
            logger.warning("Could not find like button")
            return False

        aria_label = (like_button.get_attribute('aria-label') or '').lower()
        if 'unlike' in aria_label or 'liked' in aria_label:
            logger.info("Already liked this post")
            return True

        if safe_click(driver, like_button):
            random_delay(0.5, 1)
            logger.info("Post liked")
            return True

        logger.warning("Could not click like button")
        return False

    except Exception as e:
        logger.error(f"Error liking: {e}")
        return False


def follow_user(driver, username):
    """Follow a user."""
    try:
        logger.info(f"Following @{username}")
        driver.get(f"https://www.tiktok.com/@{username}")
        random_delay(2, 3)
        dismiss_popups(driver)

        follow_selectors = [
            (By.CSS_SELECTOR, 'button[data-e2e="follow-button"]'),
            (By.XPATH, "//button[contains(@data-e2e, 'follow-button')]"),
            (By.XPATH, "//button[contains(., 'Follow') and not(contains(., 'Following'))]"),
        ]

        follow_button = None
        for by, value in follow_selectors:
            follow_button = safe_find_clickable(driver, by, value, timeout=8)
            if follow_button:
                break

        if not follow_button:
            logger.warning("Could not find follow button")
            return False

        button_text = (follow_button.text or '').lower()
        if 'following' in button_text or 'friends' in button_text:
            logger.info("Already following this user")
            return True

        if safe_click(driver, follow_button):
            random_delay(1, 2)
            logger.info(f"Now following @{username}")
            return True

        logger.warning("Could not click follow button")
        return False

    except Exception as e:
        logger.error(f"Error following: {e}")
        return False


def process_user(driver, username, comments, config):
    """Process a single follower: comment on latest, like recent posts, follow."""
    logger.info(f"Processing @{username}")

    try:
        max_likes = config['automation']['max_likes']
        posts = get_latest_posts(
            driver, username, max(config['automation']['posts_to_check'], max_likes)
        )
        if not posts:
            logger.warning(f"No posts found for @{username}")
            return {'success': False, 'reason': 'No posts'}

        comment_text = (
            random.choice(comments)
            if config['messages']['use_random_comment']
            else comments[0]
        )

        logger.info(f"Step 1/3: Commenting on latest post for @{username}")
        comment_success = comment_on_post(driver, posts[0], comment_text)
        random_delay(
            config['automation'].get('action_delay', 1),
            config['automation'].get('action_delay', 1) + 1,
        )

        likes_count = min(len(posts), max_likes)
        likes_success = 0
        logger.info(f"Step 2/3: Liking {likes_count} latest posts for @{username}")
        for i in range(likes_count):
            if like_post(driver, posts[i]):
                likes_success += 1
            random_delay(1, 2)

        logger.info(f"Step 3/3: Following @{username}")
        follow_success = follow_user(driver, username)

        success = comment_success or likes_success > 0 or follow_success
        return {
            'success': success,
            'username': username,
            'comment_used': comment_text if comment_success else None,
            'likes_done': likes_success,
            'followed': follow_success,
        }

    except Exception as e:
        logger.error(f"Error processing @{username}: {e}")
        return {'success': False, 'reason': str(e)}
