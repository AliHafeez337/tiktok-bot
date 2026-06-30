
# How to Use Dynamic Targets

## Quick Start

### 1. Create target.txt
Create a file called `target.txt` in your bot folder with:
```
charlidamelio
```

### 2. Start the bot
```bash
python main.py
```

For multiple TikTok accounts in parallel, use a different Chrome profile per terminal:
```bash
python main.py --profile account1
python main.py --profile account2
```
See [README.md](README.md) for full CLI options.

### 3. Change target while running
Open `target.txt`, change to:
```
tiktok
```
Save file. Bot will automatically switch!

---

## How It Works

**Bot checks target.txt every 30 seconds**

```
30 sec  → "Still processing @charlidamelio"
30 sec  → "Still processing @charlidamelio"
30 sec  → "🔍 Checking target file..."
        → "New target found: @tiktok"
        → "🔄 Switching to @tiktok"
        → "Resetting progress..."
        → "Starting fresh"
```

---

## Example Scenarios

### Scenario 1: Process multiple profiles overnight

**Setup:**
1. Create `target.txt` with first profile
2. Start bot
3. Go to sleep

**While bot runs:**
```
Bot processes @profile1
Bot finishes @profile1
Bot checks target.txt
Sees it's still @profile1
Stops (no more to process)
```

**To process multiple profiles:**
1. When you wake up, check progress
2. Change target.txt to @profile2
3. Bot automatically starts processing @profile2

---

### Scenario 2: Stop after current profile

**To stop gracefully:**
1. Bot is processing @profile1
2. Change target.txt to @profile1 (same as current)
3. Bot finishes @profile1
4. Bot checks target.txt
5. Sees same target
6. Stops automatically

---

## Tips

### 1. Use Comments in target.txt
```
# Process this profile
charlidamelio

# Then I'll change to this
# tiktok
```

### 2. Multiple Lines - Bot uses FIRST non-comment line
```
# First profile
charlidamelio
# Second profile (ignored until first is done)
tiktok
```

### 3. Check Current Target
Look in terminal: 
```
🎯 Current target: @charlidamelio
```

### 4. See Progress
Open `data/progress.json`
Look for `"target_profile"`

---

## Troubleshooting

### Bot not switching targets
1. Check file name is `target.txt`
2. Check file is in main bot folder
3. Check there are no spaces after username
4. Wait up to 30 seconds for bot to check

### Bot stopped unexpectedly
1. Check if you changed target to same username
2. Bot stops when no new targets
3. Change to different username to restart

### Can't change target fast enough
1. You can change target anytime
2. Bot only checks every 30 seconds
3. Wait up to 30 seconds for change

---

## Advanced: Batch Processing

Create a script to change targets automatically:

**Windows (change_target.bat):**
```batch
@echo off
echo tiktok > target.txt
echo Target changed to @tiktok
```

**Mac/Linux (change_target.sh):**
```bash
#!/bin/bash
echo "tiktok" > target.txt
echo "Target changed to @tiktok"
```

---

## FAQ

**Q: Can I change target while bot is processing a user?**
A: Yes! Bot will finish current user, then switch targets.

**Q: Will I lose progress?**
A: No! Progress is saved for each target separately.

**Q: Can I have multiple targets in one file?**
A: No, only one target at a time. But you can change anytime.

**Q: What if I delete target.txt?**
A: Bot uses default from config.yaml