import sys
import yaml
import os
import time
import random
from modules.browser_setup import get_driver, load_config
from modules.login import login_tiktok
from modules.follower_extractor import (
    extract_followers,
    extract_followers_and_following,
    extract_following,
    get_bot_username,
    get_follower_count,
    get_users_to_process,
)
from modules.action_performer import process_user
from modules.data_manager import load_progress, save_progress, load_comments
from modules.utils import (
    setup_logging, random_delay, get_timestamp,
    get_target_from_file, get_all_targets_from_file, check_target_change
)

logger = setup_logging()


def create_progress(target_username, actions_today=0):
    return {
        'started_at': get_timestamp(),
        'target_profile': target_username,
        'processed_count': 0,
        'total_found': 0,
        'current_index': 0,
        'failed_users': [],
        'processed_users': [],
        'actions_today': actions_today
    }


def process_profile(driver, target_username, config, comments, progress, max_scrolls=15):
    """Process a single profile - extract followers and process users"""
    logger.info(f"\n{'='*50}")
    logger.info(f"📊 Processing profile: @{target_username}")
    logger.info(f"{'='*50}")
    
    # Get follower count for logging
    follower_count = get_follower_count(driver, target_username)
    logger.info(f"📈 @{target_username} has {follower_count} followers")
    
    filter_mode = config['automation'].get('follower_filter', 'all')
    following = []
    bot_following = []

    if filter_mode == 'not_followed_by_target':
        followers, following = extract_followers_and_following(
            driver, target_username, max_scrolls=max_scrolls
        )
    else:
        followers = extract_followers(driver, target_username, max_scrolls=max_scrolls)
        if filter_mode == 'not_followed_by_bot':
            bot_username = get_bot_username(driver)
            if bot_username:
                bot_following = extract_following(
                    driver, bot_username, max_scrolls=max_scrolls
                )
            else:
                logger.warning(
                    "Could not detect bot account; processing all followers instead"
                )
                filter_mode = 'all'

    if not followers:
        logger.error(f"❌ Could not extract followers from @{target_username}")
        return progress, False

    progress['total_found'] = len(followers)

    users_queue = get_users_to_process(
        followers,
        following=following,
        bot_following=bot_following,
        filter_mode=filter_mode,
    )

    skip_profiles = set(config['safety']['skip_profiles']) | {target_username}
    processed_users = {u['username'] for u in progress['processed_users']}
    users_to_process = [
        u for u in users_queue
        if u not in skip_profiles and u not in processed_users
    ]

    logger.info(f"📋 Found {len(users_to_process)} followers to process")

    if not users_to_process:
        logger.info("✅ No followers left to process for this profile!")
        return progress, True

    max_users = config['automation']['max_users_per_run']
    users_to_process = users_to_process[:max_users]
    
    # Process each user
    for index, username in enumerate(users_to_process, 1):
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing {index}/{len(users_to_process)}: @{username}")
        logger.info(f"{'='*50}")
        
        # Check daily limit
        if progress['actions_today'] >= config['safety']['max_daily_actions']:
            logger.warning("⚠️ Daily action limit reached. Stopping.")
            break
        
        # Process user
        result = process_user(driver, username, comments, config)
        
        # Save result
        if result['success']:
            progress['processed_users'].append({
                'username': username,
                'action': 'processed',
                'timestamp': get_timestamp(),
                'comment_used': result.get('comment_used'),
                'likes_done': result.get('likes_done', 0),
                'followed': result.get('followed', False)
            })
            progress['processed_count'] += 1
            progress['actions_today'] += 2 + result.get('likes_done', 0)
        else:
            progress['failed_users'].append({
                'username': username,
                'reason': result.get('reason', 'Unknown error'),
                'timestamp': get_timestamp()
            })
        
        # Save progress after each user
        save_progress(progress)
        
        # Random delay between users
        delay = random.uniform(
            config['automation']['min_delay'],
            config['automation']['max_delay']
        )
        logger.info(f"⏳ Waiting {delay:.1f} seconds before next user...")
        time.sleep(delay)
    
    return progress, True

def main():
    # Setup
    logger.info("=" * 50)
    logger.info("🚀 TikTok Automation Bot Starting")
    logger.info("=" * 50)
    
    # Load config
    logger.info("Loading configuration...")
    config = load_config()
    
    # Create necessary directories
    os.makedirs('data/logs', exist_ok=True)
    os.makedirs('sessions', exist_ok=True)
    
    # Initialize driver
    logger.info("Initializing browser...")
    driver = get_driver(config)
    progress = None

    try:
        if not login_tiktok(driver, config):
            logger.error("❌ Login failed. Exiting...")
            return

        process_all = config['target'].get('process_all', False)
        max_scrolls = config['target'].get('max_follower_scrolls', 15)

        if process_all:
            targets = get_all_targets_from_file(config)
            logger.info(f"📋 Target queue ({len(targets)}): {', '.join('@' + t for t in targets)}")
        else:
            targets = [get_target_from_file(config)]
            logger.info(f"🎯 Target: @{targets[0]}")
            logger.info(f"💡 To change target, edit {config['target']['dynamic_target_file']}")

        comments = load_comments(config['messages']['comments_file'])
        if not comments:
            logger.error("❌ No comments found! Add comments to input/comments.txt")
            return

        for current_target in targets:
            saved_progress = load_progress()
            if saved_progress and saved_progress.get('target_profile') == current_target:
                progress = saved_progress
                logger.info(f"📂 Resuming progress for @{current_target}")
                logger.info(f"📊 Already processed: {progress['processed_count']} users")
            else:
                actions_today = progress.get('actions_today', 0) if progress else 0
                progress = create_progress(current_target, actions_today)
                logger.info(f"📝 Starting fresh for @{current_target}")

            progress, completed = process_profile(
                driver, current_target, config, comments, progress, max_scrolls
            )

            if not completed:
                logger.warning(f"⚠️ Skipping @{current_target} and moving to next target")
                continue

            logger.info(f"✅ Finished processing @{current_target}")

            if progress['actions_today'] >= config['safety']['max_daily_actions']:
                logger.warning("⚠️ Daily action limit reached. Stopping.")
                break

        logger.info("\n" + "=" * 50)
        logger.info("📊 FINAL SUMMARY")
        logger.info("=" * 50)
        if progress:
            logger.info(f"Last target processed: @{progress.get('target_profile', 'none')}")
            logger.info(f"Total processed this session: {progress['processed_count']}")
            logger.info(f"Failed: {len(progress['failed_users'])}")
            logger.info(f"Actions today: {progress['actions_today']}")
        logger.info("=" * 50)

    except KeyboardInterrupt:
        logger.info("\n⏹️ Bot stopped by user. Saving progress...")
        if progress:
            save_progress(progress)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        if progress:
            save_progress(progress)
    finally:
        try:
            driver.quit()
        except Exception:
            pass
        logger.info("👋 Bot shutdown complete")

if __name__ == "__main__":
    main()