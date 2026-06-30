"""
Browser Setup Module - Configured for Chrome
"""

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
import yaml
import os

def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_driver(config):
    """Initialize and return WebDriver based on config"""
    browser = config['automation']['browser'].lower()
    headless = config['automation']['headless']
    
    if browser == 'firefox':
        # Firefox support (kept for reference)
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    
    elif browser == 'chrome':
        options = webdriver.ChromeOptions()

        login_config = config.get('login', {})
        if login_config.get('persist_session', True):
            profile_dir = os.path.abspath(
                login_config.get('profile_directory', 'sessions/chrome')
            )
            os.makedirs(profile_dir, exist_ok=True)
            options.add_argument(f'--user-data-dir={profile_dir}')
            options.add_argument('--profile-directory=Default')
        
        # Basic options
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Hide automation flags
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Disable notifications and popups
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        
        # Initialize driver
        service = ChromeService(ChromeDriverManager().install())
        try:
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            profile_dir = login_config.get('profile_directory', 'sessions/chrome')
            if 'user data directory is already in use' in str(e).lower():
                raise RuntimeError(
                    f"Chrome profile already in use: {profile_dir}\n"
                    "Close the other bot window using this profile, or pick a different "
                    "--profile name."
                ) from e
            raise
        
        # Remove webdriver property to hide automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    else:
        raise ValueError(f"Unsupported browser: {browser}")