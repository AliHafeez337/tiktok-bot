# TikTok Automation Bot - Testing Guide

## 📋 TESTING GUIDE (One Document)

---

## WHAT WE'RE TESTING

We need to make sure the bot works correctly before you start using it. I'll guide you through testing step by step.

---

## BEFORE YOU START TESTING

### What You Need:
1. **A computer** (Windows, Mac, or Linux)
2. **Internet connection**
3. **A TikTok account** (preferably a test account, not your main one)
4. **10-15 minutes** of your time

### Create a Test Account (Important!)
1. Go to TikTok.com
2. Click "Sign up"
3. Create a new account (use a different email than your main)
4. **Do NOT use your main account for testing**
5. Follow 5-10 random accounts
6. Get 5-10 followers (ask friends or create fake accounts)
7. Post at least 3 videos

---

## TEST 1: LOGIN TEST

**Goal:** Make sure the bot can log in to TikTok

### Steps:
1. Open `config.yaml` file
2. Find these lines:
   ```yaml
   account:
     email: "your_email@gmail.com"
     password: "your_password"
   ```
3. Replace with your TEST ACCOUNT credentials
4. Save the file
5. Open Command Prompt/Terminal
6. Type: `cd Desktop/tiktok_bot` (or wherever your bot is)
7. Type: `python main.py`

### What Should Happen:
- [ ] A Firefox/Chrome browser opens
- [ ] It goes to TikTok login page
- [ ] It types your email
- [ ] It types your password
- [ ] It clicks login
- [ ] You see "✅ Login successful!" in the terminal

### What If It Fails:
- Check your email and password in config.yaml
- Try logging in manually in the browser first
- Make sure TikTok isn't blocking you
- Try again

### Stop the Bot:
- Press `Ctrl + C` on your keyboard
- The browser will close

### ✅ Test 1 Passed if:
- You saw "Login successful!" message
- No error messages appeared

---

## TEST 2: FIND FOLLOWERS TEST

**Goal:** Make sure the bot can find followers

### Steps:
1. Keep the bot running from Test 1
2. It will automatically go to the target profile
3. It will start extracting followers

### What Should Happen:
- [ ] Bot goes to profile page
- [ ] It clicks on "Followers"
- [ ] It starts scrolling and finding usernames
- [ ] You see numbers increasing: "Found 10 followers so far..."
- [ ] Eventually it says "✅ Extracted X followers"

### What If It Fails:
- The profile might be private (use a public profile)
- Check if username is spelled correctly
- Try a different profile

### Stop the Bot:
- Press `Ctrl + C`
- The browser will close

### ✅ Test 2 Passed if:
- Bot found at least 5 followers
- No errors appeared

---

## TEST 3: PROCESS ONE USER TEST

**Goal:** Make sure the bot can process one user completely

### Steps:
1. Open `config.yaml`
2. Find this line:
   ```yaml
   max_users_per_run: 50
   ```
3. Change it to:
   ```yaml
   max_users_per_run: 1
   ```
4. Save the file
5. Open `input/comments.txt`
6. Add at least 3 comments (one per line):
   ```
   Great video!
   Love this!
   Amazing!
   ```
7. Save the file
8. Run: `python main.py`

### What Should Happen:
- [ ] Bot logs in
- [ ] Bot finds followers
- [ ] Bot finds who's not following back
- [ ] Bot picks ONE user
- [ ] Bot goes to their profile
- [ ] Bot finds their latest video
- [ ] Bot posts your comment
- [ ] Bot likes the video
- [ ] Bot likes 2 more videos
- [ ] Bot follows the user
- [ ] Bot says "✅ Now following @username"

### Check Manually:
1. Open TikTok in your browser
2. Go to the user's profile
3. Check if your comment appears
4. Check if your likes are there
5. Check if you're following them

### ✅ Test 3 Passed if:
- All actions completed successfully
- You can see the comment, likes, and follow in the app

---

## TEST 4: PROCESS MULTIPLE USERS TEST

**Goal:** Make sure bot can handle multiple users

### Steps:
1. Open `config.yaml`
2. Change to:
   ```yaml
   max_users_per_run: 3
   ```
3. Save the file
4. Run: `python main.py`

### What Should Happen:
- [ ] Bot processes 3 users
- [ ] Between users, it waits 30-60 seconds
- [ ] It shows progress: "Processing 1/3", "Processing 2/3", etc.
- [ ] It saves progress after each user

### Check Progress File:
1. Open `data/progress.json`
2. Look for `"processed_count"`
3. It should say 3
4. Look for `"processed_users"`
5. It should list all 3 users with details

### ✅ Test 4 Passed if:
- All 3 users processed
- Progress saved correctly
- No errors

---

## TEST 5: RESUME FUNCTION TEST

**Goal:** Make sure bot continues from where it stopped

### Steps:
1. While bot is running (processing users), press `Ctrl + C`
2. It will save progress and close
3. Run: `python main.py` again

### What Should Happen:
- [ ] Bot starts normally
- [ ] It loads previous progress
- [ ] It SKIPS already processed users
- [ ] It continues with new users

### Check:
1. Open `data/progress.json`
2. See if processed_count increased
3. Make sure no duplicate users were processed

### ✅ Test 5 Passed if:
- Bot continued from where it stopped
- No users processed twice

---

## TEST 6: DAILY LIMIT TEST

**Goal:** Make sure bot stops at daily limit

### Steps:
1. Open `config.yaml`
2. Find:
   ```yaml
   max_daily_actions: 300
   ```
3. Change to:
   ```yaml
   max_daily_actions: 5
   ```
4. Save file
5. Run: `python main.py`

### What Should Happen:
- [ ] Bot processes users until it reaches 5 actions
- [ ] It says "⚠️ Daily action limit reached"
- [ ] It stops processing
- [ ] It saves progress

### ✅ Test 6 Passed if:
- Bot stopped at exactly 5 actions
- Warning message appeared
- Progress saved

---

## TEST 7: COMMENT ROTATION TEST

**Goal:** Make sure different comments are used

### Steps:
1. Open `input/comments.txt`
2. Add 5 different comments:
   ```
   Comment 1
   Comment 2
   Comment 3
   Comment 4
   Comment 5
   ```
3. Set `max_users_per_run: 10`
4. Run: `python main.py`

### What Should Happen:
- [ ] Different comments are used
- [ ] Comments are random
- [ ] All comments get used eventually

### Check:
1. Open `data/progress.json`
2. Look at `"processed_users"`
3. Check the `"comment_used"` field for each
4. Verify different comments were used

### ✅ Test 7 Passed if:
- Multiple different comments used
- No errors

---

## TEST 8: ERROR HANDLING TEST

**Goal:** Make sure bot handles errors gracefully

### Steps:
1. Test with a PRIVATE profile
   - Open `config.yaml`
   - Set target to a private account
   - Run: `python main.py`

### What Should Happen:
- [ ] Bot tries to get followers
- [ ] It can't because profile is private
- [ ] It logs error
- [ ] It doesn't crash
- [ ] It exits gracefully

### ✅ Test 8 Passed if:
- Bot didn't crash
- Error message appeared
- Bot closed properly

---

## TEST RESULTS FORM

Copy this and fill it out:

```
TEST RESULTS

Test 1 (Login): [PASS/FAIL]
Notes: _______________

Test 2 (Find Followers): [PASS/FAIL]
Notes: _______________

Test 3 (Process One User): [PASS/FAIL]
Notes: _______________

Test 4 (Process Multiple): [PASS/FAIL]
Notes: _______________

Test 5 (Resume): [PASS/FAIL]
Notes: _______________

Test 6 (Daily Limit): [PASS/FAIL]
Notes: _______________

Test 7 (Comment Rotation): [PASS/FAIL]
Notes: _______________

Test 8 (Error Handling): [PASS/FAIL]
Notes: _______________

OVERALL: [READY TO USE / NEEDS FIXES]
```

---

## WHAT TO DO IF TESTS FAIL

### If Login Fails:
1. Check credentials
2. Try logging in manually
3. Check if TikTok is blocking

### If Followers Not Found:
1. Use a public profile
2. Check username spelling
3. Try a different profile

### If Comments Not Posting:
1. Make sure comments.txt has comments
2. Check if TikTok changed the UI
3. Try with different comment text

### If Nothing Works:
1. Delete `data/progress.json`
2. Re-run setup script
3. Restart computer
4. Try again

---

## AFTER ALL TESTS PASS

### You're Ready to Use the Bot!

1. **Switch to your real account:**
   - Open `config.yaml`
   - Change email/password to your REAL account

2. **Set your target:**
   - Change `username` to the profile you want

3. **Adjust settings:**
   - Set `max_users_per_run: 50` (or however many)
   - Set `min_delay: 60` (for safety)
   - Set `max_delay: 120` (for safety)

4. **Add your real comments:**
   - Open `input/comments.txt`
   - Add your own comments

5. **Run the bot:**
   - `python main.py`

---

## QUICK REFERENCE

### Start Bot:
```
python main.py
```

### Stop Bot:
```
Ctrl + C
```

### Start Fresh (Delete Progress):
```
delete data/progress.json
```

### Check Logs:
```
open data/logs/bot.log
```

### Check Progress:
```
open data/progress.json
```

---

## FINAL CHECKLIST

Before you start testing:
- [ ] Python installed
- [ ] Bot files downloaded
- [ ] config.yaml filled
- [ ] comments.txt has comments

During testing:
- [ ] Use TEST account
- [ ] Follow steps exactly
- [ ] Watch what happens
- [ ] Note any errors

After testing:
- [ ] All tests pass
- [ ] Ready for real use
- [ ] Understand how to run
- [ ] Know how to stop

---

## QUESTIONS TO ASK ME

If anything is unclear, ask me:

1. "What does this error mean?"
2. "How do I fix this problem?"
3. "Is this working correctly?"
4. "What should I do next?"

---

**End of Testing Guide**

Ready to start testing? Let me know and we'll begin with Test 1!