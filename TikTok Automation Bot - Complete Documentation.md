# TikTok Automation Bot - Complete Documentation & Guidelines

## 1. PROJECT UNDERSTANDING

### What the Bot Does:
- **Login** to TikTok web version
- **Extract** followers from a given profile
- **Filter** to find users the bot's account doesn't follow back
- **Interact** with each non-following user:
  - Comment on their latest post
  - Like their 3 most recent posts
  - Follow the user
- **Repeat** until all non-followers are processed

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
├── main.py                     # Entry point
│
├── modules/
│   ├── __init__.py
│   ├── login.py               # Handles TikTok login
│   ├── browser_setup.py       # Browser initialization
│   ├── follower_extractor.py  # Gets followers/following
│   ├── action_performer.py    # Comment, like, follow
│   ├── data_manager.py        # Save/load progress
│   └── utils.py               # Helper functions
│
├── data/
│   ├── progress.json          # Current progress
│   ├── processed_users.json   # Already processed
│   ├── logs/
│   │   └── bot.log            # Activity log
│   └── sessions/
│       └── session.pkl        # Browser session
│
├── input/
│   └── comments.txt           # List of comments to use
│
└── requirements.txt           # Python dependencies
```

---

## 6. CONFIGURATION FILE (config.yaml)

```yaml
# TikTok Account Credentials
account:
  email: "your_email@gmail.com"
  password: "your_password"
  # OR use mobile number
  # phone: "+1234567890"

# Target Profile
target:
  username: "target_username"  # Profile to analyze

# Automation Settings
automation:
  # Time delays (in seconds)
  min_delay: 30          # Minimum delay between users
  max_delay: 60          # Maximum delay between users
  action_delay: 3        # Delay between actions on same profile
  scroll_delay: 2        # Delay when scrolling
  
  # Limits
  max_users_per_run: 50  # Process X users per session
  max_likes: 3           # Number of posts to like
  posts_to_check: 5      # Check latest X posts for comment
  
  # Browser
  headless: false        # Set true to run without UI
  browser: "firefox"     # "firefox" or "chrome"

# Safety Settings
safety:
  max_daily_actions: 300 # Stop after X actions total
  blacklist_words: [     # Skip commenting these words
    "illegal",
    "violence"
  ]
  skip_profiles: [       # Skip specific profiles
    "user1",
    "user2"
  ]

# Messages
messages:
  comments_file: "input/comments.txt"  # File with comments
  use_random_comment: true             # Pick random or sequential

# Storage
storage:
  data_directory: "data"
  log_level: "INFO"    # DEBUG, INFO, WARNING, ERROR
```

---

## 7. DATA FILES

### progress.json
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
2. Fill in your TikTok email and password
3. Put target username
4. Save the file

#### Step 6: Add Comments
1. Open `comments.txt`
2. Add your comments (one per line)
3. Save the file

#### Step 7: Run the Bot
1. Open Command Prompt/Terminal
2. Type: `cd Desktop/tiktok_bot`
3. Type: `python main.py`
4. Watch it work!

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
- progress.json (progress)
- data/ folder (all data)
- input/ folder (your comments)
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
2. **Multiple accounts** - Manage several profiles
3. **AI comments** - Generate smart comments
4. **GUI interface** - Visual dashboard
5. **Email reports** - Daily summaries
6. **Cloud hosting** - Run 24/7

### Version History:
- **v1.0**: Basic functionality
- **v1.1**: Add retry mechanism
- **v1.2**: Better error handling
- **v1.3**: Session persistence
- **v1.4**: Performance improvements

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

**Version 1.0 | Document Date: 2026-01-15 | Author: AI Assistant**