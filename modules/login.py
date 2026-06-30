"""
TikTok Login Module - Main Entry Point
Uses MANUAL login only
"""

from .login_manual import manual_login, is_logged_in
from .utils import setup_logging

logger = setup_logging()

def login_tiktok(driver, config):
    """
    Main login function - uses MANUAL login mode
    """
    logger.info("=" * 60)
    logger.info("🔐 Starting Login Process")
    logger.info("=" * 60)
    
    # Use manual login
    return manual_login(driver, config)


def ensure_logged_in(driver, config):
    """Verify login before automation steps; prompt again if session is missing."""
    if is_logged_in(driver):
        return True
    logger.warning("⚠️ Not logged in — opening login flow before continuing...")
    return manual_login(driver, config)