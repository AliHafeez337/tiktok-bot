import argparse
import re
import sys
import yaml
import os
import time
import random
from modules.browser_setup import get_driver, load_config
from modules.login import login_tiktok, ensure_logged_in
from modules.login_manual import is_logged_in
from modules.follower_extractor import (
    extract_followers,
    extract_followers_and_following,
    extract_following,
    get_bot_username,
    get_follower_count,
    get_users_to_process,
)
from modules.action_performer import process_user
from modules.data_manager import load_progress, save_progress, load_comments, set_profile
from modules.utils import (
    setup_logging, random_delay, get_timestamp,
    get_target_from_file, get_all_targets_from_file, check_target_change
)

PROFILE_NAME_RE = re.compile(r'^[a-zA-Z0-9_-]+$')


def parse_args():
    parser = argparse.ArgumentParser(
        description='TikTok Automation Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # default profile (sessions/chrome)
  python main.py --profile account1 # separate Chrome window + saved login
  python main.py -p account2        # run a second instance in another terminal
  python main.py --list-profiles    # show available profiles

Each --profile gets its own Chrome user-data folder under sessions/.
Log in once per profile; the session is reused on later runs.
        """.strip(),
    )
    parser.add_argument(
        '-p', '--profile',
        metavar='NAME',
        help='Chrome session profile name (opens sessions/NAME with saved login)',
    )
    parser.add_argument(
        '--list-profiles',
        action='store_true',
        help='List available session profiles and exit',
    )
    return parser.parse_args()


def validate_profile_name(profile_name):
    if not PROFILE_NAME_RE.match(profile_name):
        print(
            "Invalid profile name. Use letters, numbers, underscores, or hyphens only "
            f"(got: {profile_name!r}).",
            file=sys.stderr,
        )
        sys.exit(1)


def list_profiles():
    sessions_dir = 'sessions'
    if not os.path.isdir(sessions_dir):
        print("No sessions/ directory yet. Run the bot once to create one.")
        return

    profiles = sorted(
        name for name in os.listdir(sessions_dir)
        if os.path.isdir(os.path.join(sessions_dir, name))
    )
    if not profiles:
        print("No profiles found under sessions/.")
        print("Create one by running: python main.py --profile account1")
        return

    print("Available Chrome session profiles:")
    for name in profiles:
        marker = " (default)" if name == 'chrome' else ""
        print(f"  - {name}{marker}")
    print("\nRun: python main.py --profile <name>")


def apply_profile(config, profile_name):
    """Point config at an isolated Chrome user-data directory."""
    if profile_name:
        config['login']['profile_directory'] = os.path.join('sessions', profile_name)
    return config


CLI_ARGS = parse_args()

if CLI_ARGS.list_profiles:
    list_profiles()
    sys.exit(0)

if CLI_ARGS.profile:
    validate_profile_name(CLI_ARGS.profile)

set_profile(CLI_ARGS.profile)
logger = setup_logging(profile=CLI_ARGS.profile)


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


def process_profile(
    driver, target_username, config, comments, progress, max_scrolls=15,
    session_remaining=None,
):
    """Process a single profile - extract followers and process users"""
    if not is_logged_in(driver):
        logger.error("❌ Not logged in — refusing to open target profiles.")
        return progress, False, 0, False

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
        return progress, False, 0, False

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

    logger.info(f"📋 Found {len(users_queue)} followers total, {len(users_to_process)} ready to process")

    if not users_to_process:
        logger.info("✅ No followers left to process for this profile!")
        return progress, True, 0, False

    max_users = config['automation']['max_users_per_run']
    if session_remaining is not None:
        max_users = min(max_users, session_remaining)
    batch_size = min(len(users_to_process), max_users)
    logger.info(
        f"⚙️ Processing {batch_size} of {len(users_to_process)} remaining followers "
        f"(max_users_per_run={config['automation']['max_users_per_run']}"
        f"{f', session remaining={session_remaining}' if session_remaining is not None else ''})"
    )
    users_to_process = users_to_process[:max_users]

    users_attempted = 0
    
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
        users_attempted += 1
        
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

        if session_remaining is not None:
            session_remaining -= 1
            if session_remaining <= 0:
                logger.info(
                    "🛑 Session profile limit reached (max_users_per_session). Stopping bot."
                )
                break
    
    session_limit_hit = session_remaining is not None and session_remaining <= 0
    return progress, True, users_attempted, session_limit_hit

def main():
    # Setup
    profile_label = CLI_ARGS.profile or 'default (sessions/chrome)'
    logger.info("=" * 50)
    logger.info("🚀 TikTok Automation Bot Starting")
    logger.info(f"🧑 Chrome profile: {profile_label}")
    logger.info("=" * 50)
    
    # Load config
    logger.info("Loading configuration...")
    config = load_config()
    config = apply_profile(config, CLI_ARGS.profile)
    
    # Create necessary directories
    os.makedirs('data/logs', exist_ok=True)
    os.makedirs(config['login'].get('profile_directory', 'sessions/chrome'), exist_ok=True)
    
    # Initialize driver
    logger.info("Initializing browser...")
    try:
        driver = get_driver(config)
    except RuntimeError as e:
        logger.error(str(e))
        return
    progress = None

    try:
        if not login_tiktok(driver, config):
            logger.error("❌ Login failed. Exiting...")
            return

        if not ensure_logged_in(driver, config):
            logger.error("❌ Login required before processing targets. Exiting...")
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

        session_max = config['automation'].get('max_users_per_session')
        session_processed = 0
        if session_max is not None:
            logger.info(
                f"⚙️ Session limit: {session_max} users across all targets "
                f"(max_users_per_session in config.yaml)"
            )

        session_limit_hit = False
        for current_target in targets:
            if session_max is not None and session_processed >= session_max:
                logger.info(
                    f"🛑 Session limit reached ({session_max} users). Stopping bot."
                )
                break
            saved_progress = load_progress()
            if saved_progress and saved_progress.get('target_profile') == current_target:
                progress = saved_progress
                logger.info(f"📂 Resuming progress for @{current_target}")
                logger.info(f"📊 Already processed: {progress['processed_count']} users")
            else:
                actions_today = progress.get('actions_today', 0) if progress else 0
                progress = create_progress(current_target, actions_today)
                logger.info(f"📝 Starting fresh for @{current_target}")

            session_remaining = None
            if session_max is not None:
                session_remaining = session_max - session_processed

            progress, completed, users_attempted, session_limit_hit = process_profile(
                driver, current_target, config, comments, progress, max_scrolls,
                session_remaining=session_remaining,
            )
            session_processed += users_attempted

            if not completed:
                logger.warning(f"⚠️ Skipping @{current_target} and moving to next target")
                continue

            logger.info(f"✅ Finished processing @{current_target}")

            if session_limit_hit:
                break

            if progress['actions_today'] >= config['safety']['max_daily_actions']:
                logger.warning("⚠️ Daily action limit reached. Stopping.")
                break

        logger.info("\n" + "=" * 50)
        logger.info("📊 FINAL SUMMARY")
        logger.info("=" * 50)
        if progress:
            logger.info(f"Last target processed: @{progress.get('target_profile', 'none')}")
            logger.info(f"Total users scanned this session: {session_processed}")
            if session_max is not None:
                logger.info(f"Session limit: {session_max}")
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