"""
TikTok Manual Login Module
COMPLETELY MANUAL - You login yourself
"""

from selenium.webdriver.common.by import By
from .utils import setup_logging
import time

logger = setup_logging()


def _is_logged_in(driver):
    """Check if the user is logged in."""
    logged_in_selectors = [
        '[data-e2e="profile-icon"]',
        '[data-e2e="nav-profile"]',
        'a[href*="/@"][data-e2e]',
    ]
    for selector in logged_in_selectors:
        try:
            if driver.find_elements(By.CSS_SELECTOR, selector):
                return True
        except Exception:
            pass

    try:
        if driver.find_elements(By.CSS_SELECTOR, '[data-e2e="top-login-button"]'):
            return False
    except Exception:
        pass

    current_url = driver.current_url.lower()
    if any(part in current_url for part in ("/login", "/signup")):
        return False
    if any(part in current_url for part in ("feed", "home", "foryou")):
        return True

    try:
        if driver.find_element(By.XPATH, "//a[contains(@href, '/@')]"):
            return True
    except Exception:
        pass

    return False


def manual_login(driver, config):
    """
    COMPLETELY MANUAL LOGIN
    Bot does NOTHING - you login yourself in the browser
    """
    login_config = config.get('login', {})
    poll_interval = login_config.get('poll_interval', 3)
    max_wait = login_config.get('max_wait', 180)
    extra_wait = login_config.get('extra_wait', 30)
    persist_session = login_config.get('persist_session', True)

    logger.info("=" * 60)
    logger.info("🔐 MANUAL LOGIN MODE")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Browser: Chrome")
    if persist_session:
        profile_dir = login_config.get('profile_directory', 'sessions/chrome')
        logger.info(f"Session profile: {profile_dir}")
    logger.info("")

    logger.info("Checking for saved login session...")
    driver.get("https://www.tiktok.com")
    time.sleep(2)

    if _is_logged_in(driver):
        logger.info("✅ Already logged in from saved session!")
        return True

    logger.info("No saved session found. Opening login page...")
    logger.info("YOU need to:")
    logger.info("  1. Enter your email")
    logger.info("  2. Enter your password")
    logger.info("  3. Click the login button")
    logger.info("  4. Complete any CAPTCHA/verification")
    logger.info("")
    logger.info("The bot will continue as soon as you're logged in.")
    logger.info("=" * 60)
    logger.info("")

    driver.get("https://www.tiktok.com/login/phone-or-email/email")

    logger.info("")
    logger.info("⏳ WAITING FOR YOU TO LOGIN MANUALLY")
    logger.info(f"Checking every {poll_interval} seconds (up to {max_wait}s)...")
    logger.info("")

    elapsed = 0
    while elapsed < max_wait:
        if _is_logged_in(driver):
            logger.info(f"✅ You're logged in! (detected after {elapsed}s)")
            return True

        time.sleep(poll_interval)
        elapsed += poll_interval

    logger.info("Checking if you're logged in...")
    if _is_logged_in(driver):
        logger.info("✅ You're logged in!")
        return True

    logger.info("")
    logger.info("=" * 60)
    logger.info("❓ Are you logged in?")
    logger.info("=" * 60)
    logger.info("Check the browser window.")
    logger.info("If you're logged in, type: yes")
    logger.info("If you need more time, type: wait")
    logger.info("If you want to stop, type: no")
    logger.info("")

    while True:
        try:
            user_input = input("👉 Are you logged in? (yes/wait/no): ").strip().lower()
        except Exception:
            logger.info("Input failed, assuming you're logged in...")
            return True

        if user_input == "yes":
            logger.info("✅ Great! Continuing with bot...")
            return True
        elif user_input == "wait":
            logger.info(f"Waiting another {extra_wait} seconds...")
            wait_elapsed = 0
            while wait_elapsed < extra_wait:
                if _is_logged_in(driver):
                    logger.info("✅ You're logged in! Continuing...")
                    return True
                time.sleep(poll_interval)
                wait_elapsed += poll_interval
            continue
        elif user_input == "no":
            logger.info("❌ Login cancelled by user.")
            return False
        else:
            logger.info("Please type: yes, wait, or no")
