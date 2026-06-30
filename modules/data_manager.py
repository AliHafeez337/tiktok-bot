# BEFORE: File didn't exist
# AFTER: Created with:
import json
import os
from .utils import get_timestamp, setup_logging

logger = setup_logging()

def load_progress():
    """Load existing progress"""
    try:
        if os.path.exists('data/progress.json'):
            with open('data/progress.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Error loading progress: {e}")
        return None

def save_progress(progress_data):
    """Save current progress"""
    try:
        progress_data['last_updated'] = get_timestamp()
        with open('data/progress.json', 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=2)
        logger.info("✅ Progress saved")
        return True
    except Exception as e:
        logger.error(f"Error saving progress: {e}")
        return False

def load_comments(file_path='input/comments.txt'):
    """Load comments from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            comments = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(comments)} comments")
        return comments
    except Exception as e:
        logger.error(f"Error loading comments: {e}")
        return []