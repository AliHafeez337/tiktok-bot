import random
import time
from datetime import datetime
import logging

def random_delay(min_sec, max_sec):
    """Wait random time between min and max seconds"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)

def setup_logging(level='INFO', profile=None):
    """Configure logging - SIMPLIFIED VERSION"""
    import os
    os.makedirs('data/logs', exist_ok=True)

    log_name = 'bot.log' if not profile else f'bot_{profile}.log'

    # Remove any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler
    file_handler = logging.FileHandler(
        os.path.join('data/logs', log_name), encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Console handler - SIMPLE VERSION
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level),
        handlers=[file_handler, console_handler]
    )
    
    return logging.getLogger(__name__)

def get_timestamp():
    """Get current timestamp as string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def safe_find_element(driver, by, value, timeout=10):
    """Safely find element with retry"""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except:
        return None


def safe_find_clickable(driver, by, value, timeout=10):
    """Wait for an element to be clickable."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    try:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    except Exception:
        return None


def safe_click(driver, element):
    """Click an element using several fallback strategies."""
    from selenium.webdriver.common.action_chains import ActionChains

    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            element,
        )
        time.sleep(0.3)
    except Exception:
        pass

    for click in (
        lambda: element.click(),
        lambda: driver.execute_script("arguments[0].click();", element),
        lambda: ActionChains(driver).move_to_element(element).pause(0.2).click().perform(),
    ):
        try:
            click()
            return True
        except Exception:
            continue
    return False


def dismiss_popups(driver):
    """Close cookie banners and other overlays that block clicks."""
    from selenium.webdriver.common.by import By

    selectors = [
        'button[data-e2e="cookie-banner-accept"]',
        'button[data-e2e="modal-close-inner-button"]',
        '[data-e2e="close-btn"]',
    ]
    for selector in selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for button in buttons:
                if button.is_displayed():
                    safe_click(driver, button)
                    time.sleep(0.5)
        except Exception:
            pass

def _read_target_lines(config):
    """Read all non-comment target usernames from the target file."""
    target_file = config['target'].get('dynamic_target_file', 'target.txt')
    targets = []

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    targets.append(line)
    except FileNotFoundError:
        pass
    except Exception as e:
        setup_logging().error(f"Error reading target file: {e}")

    return targets


def get_target_from_file(config):
    """
    Read target username from dynamic target file
    If file doesn't exist or is empty, use config default
    """
    targets = _read_target_lines(config)
    if targets:
        return targets[0]

    logger = setup_logging()
    logger.info("Target file not found or empty, using config default")
    return config['target']['username']


def get_all_targets_from_file(config):
    """Read all target usernames from the target file."""
    targets = _read_target_lines(config)
    if targets:
        return targets
    return [config['target']['username']]

def check_target_change(current_target, config):
    """
    Check if target has changed in the file
    Returns new target if changed, else None
    """
    new_target = get_target_from_file(config)
    if new_target != current_target:
        return new_target
    return None