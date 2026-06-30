"""
TikTok Login Module - Main Entry Point
Uses MANUAL login only
"""

from .login_manual import manual_login
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