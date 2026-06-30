# TikTok Automation Bot - Complete Documentation & Guidelines

## 1. PROJECT UNDERSTANDING

### What the Bot Does:
- **Login** to TikTok web version (manual login supported — you sign in in the browser)
- **Extract** followers from one or more target profiles (`target.txt`)
- **Filter** followers by mode (`all`, `not_followed_by_bot`, `not_followed_by_target`)
- **Interact** with each selected follower:
  - Comment on their latest post
  - Like up to 3 most recent posts
  - Follow the user
- **Respect limits** — per-target, per-session, and daily caps stop the bot automatically
- **Support multiple Chrome profiles** — run separate bot instances for different TikTok accounts in parallel

### Important Considerations:
- **Legal/Ethical**: TikTok's Terms of Service prohibit automation
- **Risk**: Account may get banned or shadow-banned
- **Rates**: Must implement delays to avoid detection
- **Scope**: Web version only (not mobile app)

---

## 2. TECHNOLOGY STACK

### Recommended Tech (Fast & Local):
| Component | Choice | Why |
|-----------|--------|-----|
| **Language** | Python 3.9+ | Easy, fast development, automation libraries |
| **Automation** | Selenium WebDriver | Browser automation for web version |
| **Browser** | Firefox/Chrome with WebDriver | Headless mode for speed |
| **Parsing** | BeautifulSoup4 | Extract data from pages |
| **Logging** | Python logging | Debugging and monitoring |
| **Storage** | JSON/CSV files | Simple, no database needed |
| **Config** | YAML/JSON file | Easy to change settings |

### Installation Requirements:
```
- Python 3.9 or higher
- Firefox browser OR Chrome browser
- Geckodriver (Firefox) OR Chromedriver (Chrome)
- 2GB RAM minimum
- 500MB free disk space
```

---

## 3. SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────┐
│            MAIN CONTROLLER                  │
│        (Orchestrates all steps)             │
└───────────┬────────────────────────┬────────┘
            │                        │
    ┌───────▼────────┐    ┌─────────▼────────┐
    │  LOGIN MODULE  │    │  EXTRACTION MODULE│
    │ - Email/Pass   │    │  - Get Followers  │
    │ - OTP handling │    │  - Get Following  │
    │ - Session save │    │  - Compare lists  │
    └────────────────┘    └─────────┬────────┘
                                    │
                           ┌────────▼─────────┐
                           │  ACTION MODULE   │
                           │ - Get Latest Post│
                           │ - Post Comment   │
                           │ - Like Posts     │
                           │ - Follow User    │
                           └──────────────────┘
                                    │
                           ┌────────▼─────────┐
                           │  DATA HANDLER    │
                           │ - Save progress  │
                           │ - Log actions    │
                           │ - Error recovery │
                           └──────────────────┘
```

---

## 4. DETAILED FLOWCHART

```
START
  │
  ▼
[Load Config]
  │
  ▼
[Initialize Browser]
  │
  ▼
[Login to TikTok]
  │
  ▼
[Go to Target Profile]
  │
  ▼
[Get Followers List]
  │
  ├──Scroll until all loaded
  │
  ▼
[Get Following List]  
  │
  ├──Scroll until all loaded
  │
  ▼
[Compare Lists]
  │
  ├──Find users NOT followed back
  │
  ▼
[Create Queue of Non-Followers]
  │
  ▼
┌─Loop for each user─┐
│  │                  │
│  ▼                  │
│ [Go to User Profile]│
│  │                  │
│  ▼                  │
│ [Get Latest Posts]  │
│  │                  │
│  ▼                  │
│ [Comment on Post]   │
│  │                  │
│  ▼                  │
│ [Like 3 Posts]      │
│  │                  │
│  ▼                  │
│ [Follow User]       │
│  │                  │
│  ▼                  │
│ [Save Progress]     │
│  │                  │
│  ▼                  │
│ [Random Delay]      │
└──┤                  │
   │                  │
   ▼                  │
[END]─────────────────┘
```

---

## 5. FILE STRUCTURE

```
tiktok_bot/
│
├── config.yaml                 # All user settings
├── target.txt                  # Target usernames (one per line)
├── main.py                     # Entry point (supports --profile CLI)
│
├── modules/
│   ├── __init__.py
│   ├── login.py               # Handles TikTok login
│   ├── login_manual.py        # Manual login flow
│   ├── browser_setup.py       # Browser initialization
│   ├── follower_extractor.py  # Gets followers/following
│   ├── action_performer.py    # Comment, like, follow
│   ├── data_manager.py        # Save/load progress (per profile)
│   └── utils.py               # Helper functions
│
├── data/
│   ├── progress.json          # Progress for default profile
│   ├── progress_<name>.json   # Progress when using --profile <name>
│   └── logs/
│       ├── bot.log            # Default profile log
│       └── bot_<name>.log     # Log when using --profile <name>
│
├── sessions/
│   ├── chrome/                # Default Chrome user-data (saved login)
│   └── <profile_name>/        # One folder per --profile name
│
├── input/
│   └── comments.txt           # List of comments to use
│
├── setup.bat / setup.sh       # One-step setup scripts
└── requirements.txt           # Python dependencies
```

---

## 6. CONFIGURATION FILE (config.yaml)

```yaml
# TikTok Account Credentials (used for automated login; manual mode ignores these)
account:
  email: "your_email@gmail.com"
  password: "your_password"

# Target Profile
target:
  username: "tiktok"              # Fallback if target.txt is empty
  dynamic_target_file: "target.txt" # File with usernames to process
  process_all: true                 # Process every username in target.txt
  max_follower_scrolls: 15          # Stop scrolling if no new followers found

# Login Settings
login:
  mode: "manual"                    # "manual" — you log in in the browser
  persist_session: true             # Reuse Chrome profile between runs
  profile_directory: "sessions/chrome"  # Overridden by --profile NAME
  poll_interval: 3                  # Seconds between login checks
  max_wait: 180                     # Max seconds to wait for login
  extra_wait: 30                    # Extra time if you type "wait" at prompt

# Automation Settings
automation:
  follower_filter: all              # all | not_followed_by_bot | not_followed_by_target
  min_delay: 5                      # Min seconds between users
  max_delay: 10                     # Max seconds between users
  action_delay: 1                   # Delay between actions on same profile
  scroll_delay: 0.5                 # Delay when scrolling follower lists
  max_users_per_run: 5              # Max followers to process per target account
  max_users_per_session: 20         # Max followers to scan across ALL targets while logged in
  max_likes: 3                      # Posts to like per user
  posts_to_check: 5                 # Latest posts checked for commenting
  headless: false
  browser: "chrome"                 # "chrome" or "firefox"

# Safety Settings
safety:
  max_daily_actions: 100
  blacklist_words: ["illegal", "violence"]
  skip_profiles: ["user1", "user2"]

# Messages
messages:
  comments_file: "input/comments.txt"
  use_random_comment: true

# Storage
storage:
  data_directory: "data"
  log_level: "INFO"
```

### Processing limits (how they work together)

| Setting | Scope | Example |
|---------|--------|---------|
| `max_users_per_run` | One target username in `target.txt` | Process up to 5 followers from `@brandA` |
| `max_users_per_session` | Entire run while logged in (one Chrome profile) | Stop after 20 followers total across all targets |
| `max_daily_actions` | Calendar day (tracked in progress file) | Stop after 100 comments/likes/follows combined |

If you have 3 targets in `target.txt` and each has 100 followers, setting `max_users_per_session: 20` means the bot scans 20 profiles and **stops completely** — it will not move on to process all followers from every target.

### target.txt

One username per line (no `@`):

```
guiltyxapparel
brandymelvilleusa
lift_the_label
```

With `process_all: true`, the bot processes targets in file order until limits are hit.

### Follower filter modes

| Mode | Behavior |
|------|----------|
| `all` | Process every extracted follower |
| `not_followed_by_bot` | Skip followers your logged-in account already follows |
| `not_followed_by_target` | Skip followers the target profile already follows back |

### Multi-profile CLI

Run separate bot instances for different TikTok accounts:

```bash
python main.py                      # default: sessions/chrome
python main.py --profile account1   # sessions/account1
python main.py --profile account2   # sessions/account2
python main.py --list-profiles      # list saved profiles
```

Each profile gets:
- Its own Chrome user-data folder under `sessions/<name>/`
- Its own progress file: `data/progress_<name>.json` (default uses `data/progress.json`)
- Its own log file: `data/logs/bot_<name>.log` (default uses `data/logs/bot.log`)

Log in once per profile in the browser; subsequent runs reuse the saved session.

**Rules:**
- Use a **different** `--profile` name in each terminal when running bots in parallel.
- Do **not** start two bots with the same profile at once — Chrome locks the profile folder and the second instance will fail.
- Profile names: letters, numbers, underscores, hyphens only (e.g. `account1`, `ali_main`).

---

## 7. DATA FILES

### progress.json (and per-profile variants)

Default run writes `data/progress.json`. With `--profile account1`, progress is saved to `data/progress_account1.json` so parallel bots do not overwrite each other.

```json
{
  "started_at": "2026-01-15 10:30:00",
  "last_updated": "2026-01-15 11:45:00",
  "target_profile": "example_user",
  "processed_count": 25,
  "total_found": 150,
  "current_index": 25,
  "failed_users": ["problem_user1", "problem_user2"],
  "processed_users": [
    {
      "username": "user1",
      "action": "follow",
      "timestamp": "2026-01-15 10:35:00",
      "comment_used": "Great content!"
    }
  ]
}
```

### comments.txt
```
Amazing video! 🔥
Love your content!
Keep up the great work!
You're doing awesome!
This is fantastic!
Great post! 👏
```

---

## 8. TECHNICAL IMPLEMENTATION STEPS

### Phase 1: Project Setup (Day 1)
1. Install Python and required libraries
2. Install WebDriver for browser
3. Create project folder structure
4. Set up virtual environment

### Phase 2: Core Modules (Day 2-3)
1. **Browser Setup Module**
   - Initialize browser with options
   - Support headless mode
   - Handle WebDriver paths

2. **Login Module**
   - Navigate to TikTok
   - Enter credentials
   - Handle 2FA if exists
   - Save session cookie

3. **Follower Extractor Module**
   - Navigate to profile
   - Open followers list
   - Scroll until all loaded
   - Extract usernames
   - Same for following list
   - Compare to find non-followers

4. **Action Module**
   - Navigate to user profile
   - Find latest posts
   - Post comment on newest
   - Like 3 most recent
   - Click follow button

### Phase 3: Data Management (Day 4)
1. Save progress after each action
2. Load previous progress if exists
3. Log all activities
4. Handle errors gracefully

### Phase 4: Main Controller (Day 5)
1. Orchestrate all modules
2. Implement main loop
3. Handle configuration
4. Error recovery

### Phase 5: Testing & Refinement (Day 6-7)
1. Test with small profile
2. Test with safe account
3. Adjust delays
4. Fix issues

---

## 9. ERROR HANDLING STRATEGY

### Common Errors & Solutions:

| Error | Solution |
|-------|----------|
| Login failed | Retry with new session, check credentials |
| Element not found | Wait longer, refresh page |
| Rate limited | Increase delays, stop for 30 mins |
| Network error | Retry 3 times, then skip user |
| Capcha detected | Pause, require manual intervention |
| Profile private | Skip user, log as private |
| Post not found | Skip commenting, just follow |

### Recovery Flow:
```
Error Occurs
    │
    ▼
[Retry? 3 attempts max]
    │
    ├──YES──▶ [Wait 5s, try again]
    │
    └──NO────▶ [Log error]
                    │
                    ▼
            [Skip current user]
                    │
                    ▼
            [Save progress]
                    │
                    ▼
            [Continue next user]
```

---

## 10. USER INSTRUCTIONS

### For Computer Illiterate Users:

#### Step 1: Install Python
1. Go to https://python.org/downloads/
2. Click "Download Python 3.12"
3. When download finishes, open the file
4. **IMPORTANT**: Check box that says "Add Python to PATH"
5. Click "Install Now"
6. Wait for it to finish

#### Step 2: Install Browser & Driver
**Option A: Firefox (Recommended)**
1. Install Firefox from https://www.mozilla.org/firefox/
2. Download Geckodriver from https://github.com/mozilla/geckodriver/releases
3. Download the file for your system (Windows/Linux/Mac)
4. Move the file to your Desktop

**Option B: Chrome**
1. Install Google Chrome
2. Download Chromedriver matching your Chrome version
3. Move to Desktop

#### Step 3: Setup Project
1. Create folder on Desktop called "tiktok_bot"
2. Download all files from our repository
3. Copy them to that folder

#### Step 4: Install Requirements
1. Open Command Prompt (Windows) or Terminal (Mac/Linux)
2. Type: `cd Desktop/tiktok_bot`
3. Type: `pip install -r requirements.txt`
4. Wait for installation to finish

#### Step 5: Configure
1. Open `config.yaml` in Notepad
2. Set `login.mode` to `"manual"` (recommended — you log in yourself in the browser)
3. Add target usernames to `target.txt` (one per line)
4. Set `max_users_per_run` and `max_users_per_session` to small numbers for testing
5. Save the files

#### Step 6: Add Comments
1. Open `comments.txt`
2. Add your comments (one per line)
3. Save the file

#### Step 7: Run the Bot
1. Open Command Prompt/Terminal
2. Type: `cd Desktop/tiktok_bot`
3. Type: `python main.py`
4. Log in manually in the Chrome window when prompted
5. Watch it work!

**Multiple TikTok accounts:** open a second terminal and run `python main.py --profile account2`. Each profile keeps its own login and progress.

#### Step 8: Stop the Bot
- Press `Ctrl + C` on keyboard
- It will save progress and exit

---

## 11. TESTING GUIDE

### Pre-Testing Checklist:
- [ ] Python installed correctly (`python --version`)
- [ ] Browser installed
- [ ] WebDriver file in correct place
- [ ] All Python packages installed
- [ ] config.yaml filled correctly
- [ ] Internet connection working

### Test Scenarios:

**Test 1: Browser Opens**
- Run: `python test_browser.py`
- Expected: Browser opens to Google.com
- If fails: WebDriver not installed correctly

**Test 2: Login**
- Run: `python test_login.py`
- Expected: Logs in to TikTok
- If fails: Check credentials

**Test 3: Extract Followers**
- Run: `python test_extract.py`
- Expected: Shows list of 10-20 followers
- If fails: Profile might be private

**Test 4: Full Test (With SAFE account)**
- Create test TikTok account
- Set target to that account
- Run full bot
- Verify actions were performed

### Safety Testing:
1. **Use a secondary test account** (not your main)
2. **Run on small profile** (100 followers max)
3. **Use large delays** (60-120 seconds)
4. **Monitor TikTok account for bans**
5. **Check all actions manually**

---

## 12. PERFORMANCE OPTIMIZATION

### Speed Improvements:
1. **Headless mode**: Set `headless: true` in config
2. **Batch processing**: Process in groups
3. **Caching**: Store previously extracted data

### Resource Management:
```
- Memory: ~500MB RAM
- CPU: Light usage during actions
- Network: Moderate bandwidth
- Disk: ~100MB for data
```

### Rate Limiting:
```
Actions per minute: 3-5 (with delays)
Daily limit: 300 actions (configurable)
Sleep between users: 30-60 seconds
```

---

## 13. MAINTENANCE GUIDE

### Regular Checks:
- **Daily**: Check logs for errors
- **Weekly**: Update browser drivers
- **Monthly**: Update Python packages
- **As needed**: Update config settings

### Backup:
```
Backup these files:
- config.yaml (your settings)
- data/progress.json and data/progress_*.json (progress per profile)
- data/logs/ (activity logs)
- sessions/ (saved Chrome logins — do not share publicly)
- input/ folder (your comments)
- target.txt
```

### Update Process:
1. Save current config
2. Replace files with new version
3. Keep data directory
4. Run bot again

---

## 14. TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| "WebDriver not found" | Download driver, place in project folder |
| "Login failed" | Check credentials, try manual login |
| "Bot is too slow" | Reduce delays slightly |
| "Missing elements" | Update browser/driver |
| "Can't find profile" | Check username spelling |
| "Chrome profile already in use" | Close the other bot using that `--profile`, or pick a different profile name |
| "Action got stuck" | Increase wait times |
| "Banned/Temp locked" | Stop bot, wait, reduce speed |

### Recovery Steps:
1. Save current progress
2. Close browser
3. Wait 5 minutes
4. Restart bot
5. It should continue from last point

---

## 15. FUTURE ENHANCEMENTS

### Planned Updates:
1. **Proxy support** - Use different IPs
2. **AI comments** - Generate smart comments
3. **GUI interface** - Visual dashboard
4. **Email reports** - Daily summaries
5. **Cloud hosting** - Run 24/7

### Version History:
- **v1.0**: Basic functionality
- **v1.1**: Add retry mechanism
- **v1.2**: Better error handling
- **v1.3**: Session persistence
- **v1.4**: Performance improvements
- **v1.5**: Manual login, `target.txt` multi-target queue, follower filter modes
- **v1.6**: `--profile` CLI for parallel Chrome sessions, per-profile progress files
- **v1.7**: `max_users_per_session` — cap total scans across all targets per login

---

## 16. DISCLAIMERS

### Important Notes:
1. **USE AT YOUR OWN RISK**: This bot can get accounts banned
2. **For educational purposes only**
3. **Respect TikTok's Terms of Service**
4. **Don't spam or abuse**
5. **Monitor your account regularly**

### Best Practices:
- Use a secondary account
- Don't run 24/7
- Keep delays random
- Don't use offensive comments
- Monitor for bans
- Stop if TikTok warns you

---

## 17. SUPPORT & FURTHER HELP

### For Updates:
1. Check back for new versions
2. Review changelog
3. Update configuration
4. Test before full run

### Community:
- Join Discord server (if exists)
- Report issues on GitHub
- Share tips and tricks
- Help other users

### Documentation:
- Keep this guide updated
- Document any changes
- Save configuration examples
- Track what works

---

## 18. APPROVAL CHECKLIST

Before you approve this document:
- [ ] Understand what the bot does
- [ ] Accept the risks involved
- [ ] Have a secondary TikTok account ready
- [ ] Understand the installation process
- [ ] Know what to do if something goes wrong
- [ ] Ready to test with small numbers first

---

## 19. NEXT STEPS

### After Approval:
1. **Review and customize config.yaml**
2. **Set up comments.txt** with your messages
3. **Install all required software**
4. **Run initial test** with test account
5. **Monitor first session** carefully
6. **Adjust settings** based on results

### Development Handoff:
When you provide this document back:
- I'll start development
- Provide daily progress updates
- Share test results
- Deliver final working version

---

## 20. CONTACT & SUPPORT

**For questions before approval:**
- Review this document thoroughly
- Ask any clarifying questions
- Request specific changes

**After development starts:**
- Regular progress updates
- Testing assistance
- Troubleshooting support
- Final delivery instructions

---

**END OF DOCUMENTATION**

---

### FOR DEVELOPER (To be added after approval):

## Additional Technical Details

### Selenium Selector Examples:
```python
# Login
email_field = driver.find_element(By.NAME, "email")
password_field = driver.find_element(By.NAME, "password")

# Follower extraction
follower_elements = driver.find_elements(By.CSS_SELECTOR, ".follower-item")

# Actions
like_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='like']")
follow_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='follow']")
```

### Wait Strategies:
```python
# Implicit wait
driver.implicitly_wait(10)

# Explicit wait
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "element-id"))
)
```

### Randomization:
```python
# Random delays
delay = random.uniform(30, 60)
time.sleep(delay)

# Random comments
comment = random.choice(comment_list)
```

---

**Version 1.7 | Document Date: 2026-06-30**