# TikTok Automation Bot

Automates TikTok web interactions: log in, extract followers from target profiles, and engage with users (comment, like posts, follow).

## Quick Start

### 1. Install Python
Download Python 3.9+ from [python.org](https://python.org/downloads/). Check **Add Python to PATH** during install.

### 2. Install dependencies
**Windows:** run `setup.bat`  
**Mac/Linux:** run `bash setup.sh`

### 3. Configure
Edit `config.yaml`:
- Set login mode (`manual` recommended — you log in in the browser)
- Adjust delays and limits (see below)
- Set `follower_filter` if you want to skip certain followers

Edit `target.txt` — one TikTok username per line (used when `process_all: true`).

### 4. Add comments
Edit `input/comments.txt` — one comment per line.

### 5. Run
```bash
python main.py
```

## CLI options

| Command | Description |
|---------|-------------|
| `python main.py` | Default Chrome profile (`sessions/chrome`) |
| `python main.py --profile account1` | Separate Chrome window + saved login |
| `python main.py -p account2` | Short form of `--profile` |
| `python main.py --list-profiles` | List available session profiles |

Each `--profile` gets its own folder under `sessions/` and its own progress file under `data/`. Log in once per profile; the session is reused on later runs.

**Multiple accounts in parallel:**
```bash
# Terminal 1
python main.py --profile ali1

# Terminal 2
python main.py --profile ali2
```

## Key settings

| Setting | Scope | Description |
|---------|--------|-------------|
| `max_users_per_run` | Per target in `target.txt` | Max followers to process for one target account |
| `max_users_per_session` | Per login (Chrome profile) | Max followers to scan **across all targets** before the bot stops |
| `max_daily_actions` | Per day | Stops when total actions (comments, likes, follows) hit the cap |
| `follower_filter` | Per target | `all`, `not_followed_by_bot`, or `not_followed_by_target` |

**Example:** 5 targets in `target.txt`, each with 100 followers. With `max_users_per_session: 20`, the bot scans 20 profiles total and then exits — it does not continue to the remaining targets.

## Target list

Put usernames in `target.txt` (no `@`):

```
guiltyxapparel
brandymelvilleusa
lift_the_label
```

Set `process_all: true` in `config.yaml` to process every line in order.

## Safety tips

- Use a secondary TikTok account for testing
- Start with low limits (`max_users_per_session: 5`, longer delays)
- Monitor your account for warnings or restrictions

## Documentation

- Full guide: [TikTok Automation Bot - Complete Documentation.md](TikTok%20Automation%20Bot%20-%20Complete%20Documentation.md)
- Testing: [TEST_PLAN.md](TEST_PLAN.md)

## Warning

Use at your own risk. Automation may violate TikTok's Terms of Service and can result in account restrictions or bans.
