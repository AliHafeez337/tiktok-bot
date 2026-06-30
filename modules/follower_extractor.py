from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import (
    safe_find_element,
    safe_find_clickable,
    safe_click,
    dismiss_popups,
    random_delay,
    setup_logging,
)
import re
import time

logger = setup_logging()

INVALID_USERNAMES = {
    'login', 'signup', 'explore', 'discover', 'live', 'about', 'legal',
    'privacy', 'terms', 'support', 'feedback', 'upload', 'setting',
    'following', 'followers', 'video', 'photo', 'music', 'tag', 'search',
}


USERNAME_PATTERN = re.compile(r'/@([^/?#]+)')


def _is_valid_username(name):
    if not name:
        return False
    lowered = name.lower().strip().lstrip('@')
    if lowered in INVALID_USERNAMES:
        return False
    if not re.match(r'^[A-Za-z0-9._-]{2,}$', lowered):
        return False
    return True


def _username_from_href(href):
    if not href:
        return None
    match = USERNAME_PATTERN.search(href)
    return match.group(1) if match else None


def _navigate_to_profile(driver, username):
    """Open a TikTok profile and wait for it to load."""
    driver.get(f"https://www.tiktok.com/@{username}")
    random_delay(2, 3)
    dismiss_popups(driver)

    profile_loaded = safe_find_element(
        driver,
        By.CSS_SELECTOR,
        'h1[data-e2e="user-title"], h2[data-e2e="user-subtitle"], [data-e2e="user-page"]',
        timeout=15,
    )
    if not profile_loaded:
        logger.warning(f"Profile page may not have fully loaded for @{username}")
    return profile_loaded is not None


def _close_modal(driver):
    """Close an open followers/following modal."""
    selectors = [
        '[data-e2e="modal-close-inner-button"]',
        '[data-e2e="close-icon"]',
        'button[aria-label="Close"]',
    ]
    for selector in selectors:
        try:
            for button in driver.find_elements(By.CSS_SELECTOR, selector):
                if button.is_displayed():
                    safe_click(driver, button)
                    random_delay(0.5, 1)
                    return True
        except Exception:
            pass

    try:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        random_delay(0.5, 1)
    except Exception:
        pass
    return False


def _find_profile_stat(driver, stat_e2e):
    """Find the clickable followers/following count on a profile."""
    selectors = [
        (By.CSS_SELECTOR, f'[data-e2e="{stat_e2e}"]'),
        (By.CSS_SELECTOR, f'strong[data-e2e="{stat_e2e}"]'),
        (By.CSS_SELECTOR, f'[data-e2e="{stat_e2e}"] strong'),
        (By.XPATH, f'//strong[@data-e2e="{stat_e2e}"]'),
        (By.XPATH, f'//*[@data-e2e="{stat_e2e}"]/ancestor::*[self::a or self::button or @role="button"][1]'),
    ]
    for by, value in selectors:
        element = safe_find_clickable(driver, by, value, timeout=8)
        if element:
            return element
        element = safe_find_element(driver, by, value, timeout=3)
        if element:
            return element
    return None


def _wait_for_user_list_modal(driver, timeout=20):
    """Wait until follower/following rows appear in the popup."""
    item_selectors = [
        (By.CSS_SELECTOR, '[data-e2e="follow-item"]'),
        (By.CSS_SELECTOR, '[role="dialog"] [data-e2e="user-link"]'),
        (By.CSS_SELECTOR, '[role="dialog"] a[href*="/@"]'),
        (By.CSS_SELECTOR, '[class*="UserItemContainer"] a[href*="/@"]'),
    ]
    end = time.time() + timeout
    while time.time() < end:
        for by, value in item_selectors:
            elements = driver.find_elements(by, value)
            if elements:
                return True
        random_delay(0.5, 0.8)
    return False


def _wait_for_list_populated(driver, exclude=None, timeout=25):
    """Wait until at least one username appears in the open modal."""
    exclude = exclude or set()
    end = time.time() + timeout
    while time.time() < end:
        if _collect_usernames(driver, exclude=exclude):
            return True
        random_delay(1, 1.5)
    return False


def _open_user_list_modal(driver, username, stat_e2e, list_label):
    """Open followers or following popup from the current profile page."""
    _close_modal(driver)
    random_delay(0.5, 1)

    element = _find_profile_stat(driver, stat_e2e)
    if not element:
        logger.error(f"Could not find {list_label} button for @{username}")
        return False

    if not safe_click(driver, element):
        logger.error(f"Could not click {list_label} button for @{username}")
        return False

    random_delay(1.5, 2.5)
    dismiss_popups(driver)

    if not _wait_for_user_list_modal(driver, timeout=20):
        logger.error(f"Could not open {list_label} list for @{username}")
        return False

    if not _wait_for_list_populated(driver, exclude={username}, timeout=25):
        logger.warning(f"{list_label.capitalize()} modal opened but list still empty for @{username}")

    logger.info(f"Opened {list_label} list for @{username}")
    return True


def _collect_usernames(driver, exclude=None):
    """Collect usernames from the open followers/following modal."""
    exclude = exclude or set()
    usernames = []
    seen = set()

    scope_selectors = [
        '[role="dialog"]',
        '[class*="UserListContainer"]',
        '[data-e2e="follow-list"]',
    ]
    scopes = []
    for selector in scope_selectors:
        scopes.extend(driver.find_elements(By.CSS_SELECTOR, selector))

    link_selectors = [
        '[data-e2e="follow-item"] a[href*="/@"]',
        '[data-e2e="user-link"]',
        '[data-e2e="search-user-container"] a[href*="/@"]',
        '[class*="UserItemContainer"] a[href*="/@"]',
        '[class*="UserItem"] a[href*="/@"]',
        '[role="dialog"] li a[href*="/@"]',
        '[role="dialog"] a[href*="/@"]',
    ]

    search_roots = scopes if scopes else [driver.find_element(By.TAG_NAME, 'body')]
    for root in search_roots:
        for selector in link_selectors:
            try:
                for element in root.find_elements(By.CSS_SELECTOR, selector):
                    href = element.get_attribute('href')
                    username = _username_from_href(href)
                    if not username:
                        username = element.text.strip().lstrip('@')
                    username = (username or '').strip().lstrip('@')
                    if (
                        username
                        and _is_valid_username(username)
                        and username not in exclude
                        and username not in seen
                    ):
                        seen.add(username)
                        usernames.append(username)
            except Exception:
                continue

    return usernames


def _scroll_user_list(driver):
    """Scroll the followers/following modal."""
    scroll_targets = [
        '[data-e2e="follow-list"]',
        '[role="dialog"] [class*="DivUserListContainer"]',
        '[class*="UserListContainer"]',
        '[role="dialog"] ul',
        '[role="dialog"]',
    ]

    for selector in scroll_targets:
        for container in driver.find_elements(By.CSS_SELECTOR, selector):
            try:
                if container.is_displayed():
                    current = driver.execute_script("return arguments[0].scrollTop;", container)
                    driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight;",
                        container,
                    )
                    new_pos = driver.execute_script("return arguments[0].scrollTop;", container)
                    if new_pos > current:
                        return True
            except Exception:
                continue

    driver.execute_script("window.scrollBy(0, 600);")
    return False


def _extract_user_list(driver, username, stat_e2e, list_label, max_scrolls=15, no_progress_limit=6):
    """Extract usernames from an already-open profile page."""
    if not _open_user_list_modal(driver, username, stat_e2e, list_label):
        return []

    users = []
    scroll_attempts = 0
    no_progress_streak = 0

    while scroll_attempts < max_scrolls:
        batch = _collect_usernames(driver, exclude={username})
        previous_count = len(users)

        for name in batch:
            if name not in users:
                users.append(name)

        if len(users) > previous_count:
            no_progress_streak = 0
            logger.info(f"Found {len(users)} {list_label} so far...")
        else:
            no_progress_streak += 1
            if scroll_attempts < 3 and not users:
                logger.warning(f"No {list_label} found yet, waiting for list to load...")
            elif no_progress_streak >= no_progress_limit:
                logger.warning(
                    f"No new {list_label} after {no_progress_limit} scrolls, stopping early"
                )
                break

        try:
            if driver.find_element(By.XPATH, "//span[contains(text(), 'No more results')]"):
                break
        except Exception:
            pass

        _scroll_user_list(driver)
        random_delay(0.8, 1.2)
        scroll_attempts += 1

    logger.info(f"Extracted {len(users)} {list_label}")
    _close_modal(driver)
    random_delay(0.5, 1)
    return users


def _extract_lists_from_profile(driver, username, max_scrolls=15):
    """Navigate once and extract both followers and following."""
    if not _navigate_to_profile(driver, username):
        return [], []

    followers = _extract_user_list(
        driver, username, "followers-count", "followers", max_scrolls=max_scrolls
    )

    _navigate_to_profile(driver, username)
    following = _extract_user_list(
        driver, username, "following-count", "following", max_scrolls=max_scrolls
    )
    return followers, following


def extract_followers(driver, username, max_scrolls=15):
    """Extract followers of a user."""
    try:
        logger.info(f"Extracting followers for @{username}")
        followers, _ = _extract_lists_from_profile(driver, username, max_scrolls=max_scrolls)
        return followers
    except Exception as e:
        logger.error(f"Error extracting followers: {e}")
        return []


def extract_following(driver, username, max_scrolls=15):
    """Extract following list of a user."""
    try:
        logger.info(f"Extracting following for @{username}")
        _, following = _extract_lists_from_profile(driver, username, max_scrolls=max_scrolls)
        return following
    except Exception as e:
        logger.error(f"Error extracting following: {e}")
        return []


def extract_followers_and_following(driver, username, max_scrolls=15):
    """Extract followers and following in one profile visit."""
    try:
        logger.info(f"Extracting followers and following for @{username}")
        return _extract_lists_from_profile(driver, username, max_scrolls=max_scrolls)
    except Exception as e:
        logger.error(f"Error extracting lists for @{username}: {e}")
        return [], []


def get_bot_username(driver):
    """Get the logged-in account username from the navigation profile link."""
    selectors = [
        'a[data-e2e="nav-profile"]',
        '[data-e2e="profile-icon"]',
        'a[href*="/@"][data-e2e]',
    ]
    for selector in selectors:
        try:
            for element in driver.find_elements(By.CSS_SELECTOR, selector):
                href = element.get_attribute('href')
                username = _username_from_href(href)
                if username and username.lower() not in ('login', 'signup', 'explore'):
                    logger.info(f"Detected bot account: @{username}")
                    return username
        except Exception:
            continue

    try:
        driver.get('https://www.tiktok.com/profile')
        random_delay(2, 3)
        username = _username_from_href(driver.current_url)
        if username:
            logger.info(f"Detected bot account: @{username}")
            return username
    except Exception:
        pass

    logger.warning('Could not detect bot username')
    return None


def get_users_to_process(followers, following=None, bot_following=None, filter_mode='all'):
    """
    Build the queue of followers to interact with.

    filter_mode:
      - all: every extracted follower
      - not_followed_by_bot: followers the bot account has not followed yet
      - not_followed_by_target: followers the target profile has not followed back
    """
    follower_set = set(followers)

    if filter_mode == 'not_followed_by_target':
        users = list(follower_set - set(following or []))
        logger.info(
            f"Filter '{filter_mode}': {len(users)} followers not followed back by target"
        )
    elif filter_mode == 'not_followed_by_bot':
        users = list(follower_set - set(bot_following or []))
        logger.info(
            f"Filter '{filter_mode}': {len(users)} followers not yet followed by bot"
        )
    else:
        users = list(followers)
        logger.info(f"Filter '{filter_mode}': processing all {len(users)} followers")

    return users


def compare_lists(followers, following):
    """Find users not followed back by the target profile."""
    return get_users_to_process(
        followers, following=following, filter_mode='not_followed_by_target'
    )


def get_follower_count(driver, username):
    """Get the follower count of a user."""
    try:
        logger.info(f"Getting follower count for @{username}")
        _navigate_to_profile(driver, username)

        selectors = [
            (By.CSS_SELECTOR, 'strong[data-e2e="followers-count"]'),
            (By.CSS_SELECTOR, '[data-e2e="followers-count"] strong'),
            (By.CSS_SELECTOR, '[data-e2e="followers-count"]'),
            (By.XPATH, "//strong[@data-e2e='followers-count']"),
        ]

        count_text = None
        for by, value in selectors:
            element = safe_find_element(driver, by, value, timeout=5)
            if element:
                count_text = element.text.strip()
                if count_text:
                    break

        if not count_text:
            logger.warning(f"Could not read follower count for @{username}")
            return 0

        count_text = count_text.upper().replace(',', '')
        if 'K' in count_text:
            return int(float(count_text.replace('K', '')) * 1000)
        if 'M' in count_text:
            return int(float(count_text.replace('M', '')) * 1000000)
        return int(count_text)

    except Exception as e:
        logger.error(f"Error getting follower count: {e}")
        return 0
