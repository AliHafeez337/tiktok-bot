from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from .utils import safe_find_element, safe_find_clickable, safe_click, dismiss_popups, random_delay, setup_logging
import json
import random
import re
import time

logger = setup_logging()

POST_ID_PATTERN = re.compile(r'/(?:video|photo)/(\d+)')
INVALID_USERNAMES = {
    'login', 'signup', 'explore', 'discover', 'live', 'about', 'legal',
    'privacy', 'terms', 'support', 'feedback', 'upload', 'setting',
    'following', 'followers', 'video', 'photo', 'music', 'tag', 'search',
}
PROFILE_POST_ROOT_SELECTORS = [
    '[data-e2e="user-post-item-list"]',
    '[data-e2e="user-post-item-list-container"]',
    'div[class*="DivVideoFeed"]',
]
PROFILE_POST_ITEM_SELECTORS = [
    'div[data-e2e="user-post-item"]',
    'div[data-e2e="user-post-item-list"] > div',
]


def _wait_for_video_page(driver, timeout=20):
    """Wait until a TikTok video/photo page has loaded."""
    page_selectors = [
        '[data-e2e="browse-video-desc"]',
        'button[data-e2e="like-icon"]',
        'button[data-e2e="browse-like-icon"]',
        '[data-e2e="like-icon"]',
        '[data-e2e="comment-count"]',
        '[data-e2e="browse-comment-count"]',
        '[data-e2e="video-desc"]',
    ]
    end = time.time() + timeout
    while time.time() < end:
        for selector in page_selectors:
            if safe_find_element(driver, By.CSS_SELECTOR, selector, timeout=2):
                return True
        random_delay(0.5, 0.8)
    return False


def _ensure_comments_panel(driver):
    """Open the comments panel when the inline editor is not visible."""
    if _find_comment_editor(driver):
        return True

    icon_selectors = [
        'button[data-e2e="comment-icon"]',
        'span[data-e2e="comment-icon"]',
        '[data-e2e="comment-icon"]',
        '[data-e2e="browse-comment-icon"]',
    ]
    for selector in icon_selectors:
        icon = safe_find_clickable(driver, By.CSS_SELECTOR, selector, timeout=3)
        if icon:
            safe_click(driver, icon)
            random_delay(1, 2)
            break

    tab_selectors = [
        (By.CSS_SELECTOR, '[data-e2e="comment-tab"]'),
        (By.CSS_SELECTOR, '[data-e2e="browse-comment-tab"]'),
        (By.XPATH, "//*[@role='tab' and contains(., 'Comments')]"),
        (By.XPATH, "//button[contains(., 'Comments')]"),
        (By.XPATH, "//*[self::p or self::span or self::div][normalize-space()='Comments']"),
    ]
    for by, value in tab_selectors:
        tab = safe_find_clickable(driver, by, value, timeout=3)
        if tab:
            safe_click(driver, tab)
            random_delay(0.5, 1)
            logger.info("Selected Comments tab")
            return True

    return _find_comment_editor(driver) is not None


def _find_comment_editor(driver):
    """Find the inner Draft.js comment editor (not the outer container)."""
    editor_selectors = [
        (By.CSS_SELECTOR, 'div[data-e2e="comment-input"] div[contenteditable="true"]'),
        (By.CSS_SELECTOR, 'div[data-e2e="comment-text"] div[contenteditable="true"]'),
        (By.CSS_SELECTOR, 'div[data-e2e="comment-input"] [role="textbox"]'),
        (By.CSS_SELECTOR, 'div[data-e2e="browse-comment-input"] div[contenteditable="true"]'),
        (By.CSS_SELECTOR, '.public-DraftEditor-content[contenteditable="true"]'),
        (By.CSS_SELECTOR, '[class*="InputEditorContainer"] div[contenteditable="true"]'),
        (By.CSS_SELECTOR, '[class*="CommentInput"] div[contenteditable="true"]'),
        (By.XPATH, "//div[contains(@data-e2e, 'comment-input')]//div[@contenteditable='true']"),
        (By.XPATH, "//div[@contenteditable='true' and contains(@class, 'DraftEditor')]"),
    ]

    for by, value in editor_selectors:
        for element in driver.find_elements(by, value):
            try:
                if element.is_displayed() and element.is_enabled():
                    return element
            except Exception:
                continue

    return safe_find_element(
        driver,
        By.CSS_SELECTOR,
        'div[data-e2e="comment-input"] div[contenteditable="true"], '
        'div[data-e2e="browse-comment-input"] div[contenteditable="true"]',
        timeout=5,
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


def _post_id_from_url(href):
    """Extract the numeric TikTok post ID from a video/photo URL."""
    if not href:
        return None
    match = POST_ID_PATTERN.search(href.split('?')[0])
    return int(match.group(1)) if match else None


def _current_page_post_id(driver):
    """Read the post ID from the browser's current URL."""
    return _post_id_from_url(driver.current_url)


def _wait_for_correct_post_page(driver, post_url, timeout=25):
    """Wait until the browser has loaded the exact post from post_url."""
    expected_id = _post_id_from_url(post_url)
    if not expected_id:
        return False

    expected_id_str = str(expected_id)
    end = time.time() + timeout
    while time.time() < end:
        current_id = _current_page_post_id(driver)
        if current_id == expected_id and _wait_for_video_page(driver, timeout=3):
            return True
        random_delay(0.5, 0.8)

    logger.warning(
        f"Page mismatch: expected post {expected_id_str}, "
        f"got URL {driver.current_url}"
    )
    return False


def _normalize_post_url(href, username):
    """Normalize a profile post URL and ensure it belongs to the target user."""
    if not href:
        return None

    clean_href = href.split('?')[0].rstrip('/')
    post_id = _post_id_from_url(clean_href)
    if not post_id:
        return None

    lowered = clean_href.lower()
    marker = f'/@{username.lower()}/'
    if marker not in lowered:
        return None

    if '/photo/' in lowered:
        return f'https://www.tiktok.com/@{username}/photo/{post_id}'
    return f'https://www.tiktok.com/@{username}/video/{post_id}'


def _extract_posts_from_page_json(driver, username):
    """Fallback: read post IDs from TikTok's embedded page JSON."""
    links = []
    seen = set()

    def add_post_id(post_id, is_photo=False):
        if not post_id or post_id in seen:
            return
        seen.add(post_id)
        path = 'photo' if is_photo else 'video'
        links.append(f'https://www.tiktok.com/@{username}/{path}/{post_id}')

    page_source = driver.page_source
    script_patterns = [
        r'<script[^>]+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
        r'<script[^>]+id="SIGI_STATE"[^>]*>(.*?)</script>',
    ]

    for pattern in script_patterns:
        match = re.search(pattern, page_source, re.DOTALL)
        if not match:
            continue
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue

        item_lists = []
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, dict) and 'ItemList' in value:
                    item_lists.append(value['ItemList'])
            if 'ItemList' in data:
                item_lists.append(data['ItemList'])

        for item_list in item_lists:
            if not isinstance(item_list, dict):
                continue
            for list_data in item_list.values():
                if not isinstance(list_data, dict):
                    continue
                for post_id in list_data.get('list', []):
                    add_post_id(str(post_id))

        item_modules = []
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, dict) and 'ItemModule' in value:
                    item_modules.append(value['ItemModule'])
            if 'ItemModule' in data:
                item_modules.append(data['ItemModule'])

        for item_module in item_modules:
            if not isinstance(item_module, dict):
                continue
            for post_id, item in item_module.items():
                author = ''
                if isinstance(item, dict):
                    author = (
                        item.get('author', '')
                        or item.get('authorId', '')
                        or item.get('nickname', '')
                    ).lower()
                    if author and username.lower() not in author and author != username.lower():
                        continue
                    is_photo = item.get('imagePost') or '/photo/' in str(item.get('shareMeta', {}))
                else:
                    is_photo = False
                add_post_id(str(post_id), is_photo=is_photo)

        if links:
            break

    return links


def _collect_profile_post_links_dom(driver, username):
    """Collect post links in profile grid order (matches what you see on the profile)."""
    ordered_links = []
    seen = set()

    def add_link(href):
        normalized = _normalize_post_url(href, username)
        if not normalized:
            return
        post_id = _post_id_from_url(normalized)
        if post_id and post_id not in seen:
            seen.add(post_id)
            ordered_links.append(normalized)

    for item_selector in PROFILE_POST_ITEM_SELECTORS:
        items = driver.find_elements(By.CSS_SELECTOR, item_selector)
        if not items:
            continue
        for item in items:
            link = None
            for tag in ('a',):
                try:
                    anchors = item.find_elements(By.TAG_NAME, tag)
                    for anchor in anchors:
                        href = anchor.get_attribute('href') or ''
                        if '/video/' in href or '/photo/' in href:
                            link = href
                            break
                except Exception:
                    continue
            if not link:
                try:
                    href = item.get_attribute('href')
                    if href and ('/video/' in href or '/photo/' in href):
                        link = href
                except Exception:
                    pass
            add_link(link)
        if ordered_links:
            break

    if not ordered_links:
        for root_selector in PROFILE_POST_ROOT_SELECTORS:
            for root in driver.find_elements(By.CSS_SELECTOR, root_selector):
                for anchor in root.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"], a[href*="/photo/"]'):
                    add_link(anchor.get_attribute('href'))
            if ordered_links:
                break

    return ordered_links


def _ensure_videos_tab(driver):
    """Select the Videos tab on a profile when tabs are shown."""
    tab_selectors = [
        (By.CSS_SELECTOR, '[data-e2e="videos-tab"]'),
        (By.XPATH, "//p[@data-e2e='videos-tab']"),
        (By.XPATH, "//*[@role='tab' and normalize-space()='Videos']"),
        (By.XPATH, "//button[normalize-space()='Videos']"),
    ]
    for by, value in tab_selectors:
        tab = safe_find_clickable(driver, by, value, timeout=3)
        if tab:
            safe_click(driver, tab)
            random_delay(0.5, 1)
            return True
    return False


def _scroll_profile_post_grid(driver):
    """Scroll the profile page to load more posts in the grid."""
    for selector in PROFILE_POST_ROOT_SELECTORS:
        for container in driver.find_elements(By.CSS_SELECTOR, selector):
            try:
                if container.is_displayed():
                    driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight;",
                        container,
                    )
                    return True
            except Exception:
                continue

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    return False


def get_latest_posts(driver, username, count=3):
    """Get the first N posts from the profile grid (same order as shown on TikTok)."""
    try:
        logger.info(f"Getting latest posts for @{username}")
        driver.get(f"https://www.tiktok.com/@{username}")
        random_delay(2, 3)
        dismiss_popups(driver)

        safe_find_element(
            driver,
            By.CSS_SELECTOR,
            'h1[data-e2e="user-title"], h2[data-e2e="user-subtitle"], [data-e2e="user-page"]',
            timeout=15,
        )
        safe_find_element(
            driver,
            By.CSS_SELECTOR,
            'div[data-e2e="user-post-item"], [data-e2e="user-post-item-list"]',
            timeout=10,
        )
        _ensure_videos_tab(driver)
        random_delay(1, 1.5)

        posts = _collect_profile_post_links_dom(driver, username)
        if len(posts) < count:
            _scroll_profile_post_grid(driver)
            random_delay(1, 1.5)
            for link in _collect_profile_post_links_dom(driver, username):
                if link not in posts:
                    posts.append(link)

        if not posts:
            logger.info(f"DOM grid empty for @{username}, trying embedded page JSON")
            posts = _extract_posts_from_page_json(driver, username)

        if not posts:
            logger.warning(f"No profile posts found for @{username}")
            return []

        latest_posts = posts[:count]

        logger.info(f"Found {len(latest_posts)} profile posts for @{username}")
        for index, post_url in enumerate(latest_posts, start=1):
            logger.info(f"  Profile post #{index}: {post_url}")

        return latest_posts

    except Exception as e:
        logger.error(f"Error getting posts: {e}")
        return []


def _submit_comment(driver, comment_input, comment_text):
    """Click the post button or press Enter to submit a comment."""
    post_selectors = [
        (By.CSS_SELECTOR, 'button[data-e2e="comment-post"]'),
        (By.CSS_SELECTOR, 'div[data-e2e="comment-post"]'),
        (By.CSS_SELECTOR, 'button[data-e2e="browse-comment-post"]'),
        (By.XPATH, "//button[contains(@data-e2e, 'comment-post')]"),
        (By.XPATH, "//div[contains(@data-e2e, 'comment-post')]"),
        (By.XPATH, "//button[normalize-space()='Post']"),
    ]

    for by, value in post_selectors:
        post_button = safe_find_clickable(driver, by, value, timeout=3)
        if post_button and safe_click(driver, post_button):
            random_delay(1, 2)
            return True

    try:
        comment_input.send_keys(Keys.ENTER)
        random_delay(1, 2)
        return True
    except Exception:
        return False


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

        comment_input = None
        for attempt in range(3):
            comment_input = _find_comment_editor(driver)
            if comment_input:
                break

            logger.info(f"Opening comments panel (attempt {attempt + 1}/3)")
            _ensure_comments_panel(driver)
            random_delay(1.5, 2.5)
            comment_input = _find_comment_editor(driver)

        if not comment_input:
            logger.warning("Could not find comment input")
            return False

        if not _type_in_comment_editor(driver, comment_input, comment_text):
            logger.warning("Could not type into comment input")
            return False

        random_delay(0.5, 1)

        if not _submit_comment(driver, comment_input, comment_text):
            logger.warning("Could not find or click post button")
            return False

        logger.info(f"Comment posted: '{comment_text}'")
        return True

    except Exception as e:
        logger.error(f"Error commenting: {e}")
        return False


def _find_like_button(driver):
    """Find the like button on a video/photo page."""
    like_selectors = [
        (By.CSS_SELECTOR, 'button[data-e2e="like-icon"]'),
        (By.CSS_SELECTOR, 'button[data-e2e="browse-like-icon"]'),
        (By.CSS_SELECTOR, '[data-e2e="like-icon"]'),
        (By.CSS_SELECTOR, '[data-e2e="browse-like-icon"]'),
        (By.XPATH, "//button[contains(@aria-label, 'Like')]"),
        (By.XPATH, "//button[contains(@aria-label, 'like video')]"),
    ]

    for by, value in like_selectors:
        element = safe_find_clickable(driver, by, value, timeout=5)
        if not element:
            continue
        if element.tag_name.lower() == 'button':
            return element
        try:
            parent_button = element.find_element(By.XPATH, './ancestor::button[1]')
            if parent_button:
                return parent_button
        except Exception:
            pass
        return element
    return None


def _is_post_liked(like_button):
    """Detect whether TikTok shows the post as liked."""
    aria_label = (like_button.get_attribute('aria-label') or '').lower()
    aria_pressed = (like_button.get_attribute('aria-pressed') or '').lower()
    if aria_pressed == 'true':
        return True
    if 'unlike' in aria_label:
        return True

    nodes = [like_button]
    try:
        nodes.extend(like_button.find_elements(By.CSS_SELECTOR, 'svg, span, div'))
    except Exception:
        pass

    for node in nodes:
        label = (node.get_attribute('aria-label') or '').lower()
        if 'unlike' in label or 'remove like' in label:
            return True
        if 'liked' in label and 'like video' not in label:
            return True
    return False


def _poll_post_liked(driver, expected_id, timeout=6):
    """Wait briefly for a like action to register on the current post."""
    end = time.time() + timeout
    while time.time() < end:
        if _current_page_post_id(driver) != expected_id:
            return False
        like_button = _find_like_button(driver)
        if like_button and _is_post_liked(like_button):
            return True
        random_delay(0.4, 0.7)
    return False


def like_post(driver, post_url):
    """Like a post."""
    try:
        expected_id = _post_id_from_url(post_url)
        logger.info(f"Liking post: {post_url}")

        driver.get(post_url)
        random_delay(2, 3)
        dismiss_popups(driver)

        if not _wait_for_correct_post_page(driver, post_url, timeout=25):
            logger.warning(
                f"Wrong or unfinished page before like attempt "
                f"(wanted post {expected_id}, URL={driver.current_url})"
            )
            return False

        like_button = _find_like_button(driver)
        if not like_button:
            random_delay(1, 2)
            like_button = _find_like_button(driver)

        if not like_button:
            logger.warning("Could not find like button")
            return False

        if _is_post_liked(like_button):
            if _current_page_post_id(driver) == expected_id:
                logger.info("Already liked this post")
                return True
            logger.warning("Like button shows liked, but page post ID does not match target")
            return False

        if not safe_click(driver, like_button):
            logger.warning("Could not click like button")
            return False

        if _poll_post_liked(driver, expected_id):
            logger.info(f"Post liked (verified on post {expected_id})")
            return True

        # Retry once — TikTok sometimes ignores the first click on photo posts.
        refreshed = _find_like_button(driver)
        if refreshed and not _is_post_liked(refreshed):
            safe_click(driver, refreshed)
            random_delay(0.8, 1.2)
            if _poll_post_liked(driver, expected_id, timeout=4):
                logger.info(f"Post liked on retry (verified on post {expected_id})")
                return True

        logger.warning(f"Like click did not register for post {expected_id}")
        return False

    except Exception as e:
        logger.error(f"Error liking: {e}")
        return False


def _find_follow_button(driver):
    """Find the profile follow button if the user is not followed yet."""
    follow_selectors = [
        (By.CSS_SELECTOR, 'button[data-e2e="follow-button"]'),
        (By.XPATH, "//button[contains(@data-e2e, 'follow-button')]"),
        (By.XPATH, "//button[contains(., 'Follow') and not(contains(., 'Following'))]"),
    ]

    for by, value in follow_selectors:
        follow_button = safe_find_clickable(driver, by, value, timeout=8)
        if follow_button:
            return follow_button
    return None


def _is_user_followed(driver):
    """Verify the profile shows Following/Friends instead of Follow."""
    state_selectors = [
        (By.CSS_SELECTOR, 'button[data-e2e="following-button"]'),
        (By.XPATH, "//button[contains(@data-e2e, 'following-button')]"),
        (By.XPATH, "//button[normalize-space()='Following']"),
        (By.XPATH, "//button[normalize-space()='Friends']"),
    ]

    for by, value in state_selectors:
        button = safe_find_element(driver, by, value, timeout=2)
        if button and button.is_displayed():
            return True

    follow_button = safe_find_element(
        driver, By.CSS_SELECTOR, 'button[data-e2e="follow-button"]', timeout=2
    )
    if follow_button and follow_button.is_displayed():
        text = (follow_button.text or '').strip().lower()
        if 'following' in text or 'friends' in text:
            return True
        return False

    return False


def follow_user(driver, username):
    """Follow a user."""
    try:
        logger.info(f"Following @{username}")
        driver.get(f"https://www.tiktok.com/@{username}")
        random_delay(2, 3)
        dismiss_popups(driver)

        if _is_user_followed(driver):
            logger.info(f"Already following @{username}")
            return True

        follow_button = _find_follow_button(driver)
        if not follow_button:
            logger.warning("Could not find follow button")
            return False

        if not safe_click(driver, follow_button):
            logger.warning("Could not click follow button")
            return False

        random_delay(1.5, 2.5)
        dismiss_popups(driver)

        if _is_user_followed(driver):
            logger.info(f"Now following @{username} (verified)")
            return True

        # Retry once in case TikTok ignored the first click.
        follow_button = _find_follow_button(driver)
        if follow_button and safe_click(driver, follow_button):
            random_delay(1.5, 2.5)
            dismiss_popups(driver)
            if _is_user_followed(driver):
                logger.info(f"Now following @{username} (verified on retry)")
                return True

        logger.warning(f"Follow click did not register for @{username}")
        return False

    except Exception as e:
        logger.error(f"Error following: {e}")
        return False


def process_user(driver, username, comments, config):
    """Process a single follower: comment on latest, like recent posts, follow."""
    logger.info(f"Processing @{username}")

    try:
        max_likes = config['automation']['max_likes']
        posts = get_latest_posts(driver, username, max_likes)
        if not posts:
            logger.warning(f"No posts found for @{username}")
            return {'success': False, 'comment_success': False, 'reason': 'No posts'}

        comment_text = (
            random.choice(comments)
            if config['messages']['use_random_comment']
            else comments[0]
        )

        latest_post = posts[0]
        logger.info(f"Step 1/3: Commenting on first profile post for @{username}")
        logger.info(f"Target post URL: {latest_post}")
        comment_success = comment_on_post(driver, latest_post, comment_text)
        if not comment_success:
            logger.warning(
                f"Comment failed for @{username} — skipping likes and follow, moving to next follower"
            )
            return {
                'success': False,
                'username': username,
                'comment_success': False,
                'comment_used': None,
                'likes_done': 0,
                'followed': False,
                'reason': 'Comment failed',
            }

        random_delay(
            config['automation'].get('action_delay', 1),
            config['automation'].get('action_delay', 1) + 1,
        )

        likes_count = min(len(posts), max_likes)
        likes_success = 0
        logger.info(f"Step 2/3: Liking profile posts #1-#{likes_count} for @{username}")
        for i in range(likes_count):
            logger.info(f"Liking profile post #{i + 1}: {posts[i]}")
            if like_post(driver, posts[i]):
                likes_success += 1
            else:
                logger.warning(f"Failed to like profile post #{i + 1}: {posts[i]}")
            random_delay(2, 3)

        logger.info(f"Step 3/3: Following @{username}")
        follow_success = follow_user(driver, username)

        if not follow_success:
            logger.warning(f"Follow failed for @{username}")

        if likes_success < likes_count:
            logger.warning(
                f"Likes incomplete for @{username}: {likes_success}/{likes_count} "
                f"(comment ok, follow={'yes' if follow_success else 'no'})"
            )

        return {
            'success': True,
            'username': username,
            'comment_success': True,
            'comment_used': comment_text,
            'likes_done': likes_success,
            'likes_target': likes_count,
            'followed': follow_success,
            'reason': None,
        }

    except Exception as e:
        logger.error(f"Error processing @{username}: {e}")
        return {'success': False, 'comment_success': False, 'reason': str(e)}
