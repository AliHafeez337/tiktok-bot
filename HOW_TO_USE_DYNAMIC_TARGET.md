# How to Use Dynamic Targets

## Quick Start

### 1. Create target.txt
Create `target.txt` in the bot folder with one username per line (no `@`):

```
guiltyxapparel
brandymelvilleusa
lift_the_label
```

### 2. Enable multi-target mode in config.yaml
```yaml
target:
  process_all: true
  dynamic_target_file: "target.txt"
```

### 3. Start the bot
```bash
python main.py
```

For multiple TikTok accounts in parallel, use a different Chrome profile per terminal:
```bash
python main.py --profile account1
python main.py --profile account2
```

See [README.md](README.md) for full CLI options.

---

## How It Works

With `process_all: true`, the bot reads every username from `target.txt` at startup and processes them **in order**.

```
Start → Read target.txt → [@brandA, @brandB, @brandC]
      → Process @brandA followers (up to max_users_per_run)
      → Process @brandB followers
      → Process @brandC followers
      → Stop when limits are hit or all targets done
```

### Limits that affect the queue

| Setting | Effect |
|---------|--------|
| `max_users_per_run` | Max followers processed **per target** in the list |
| `max_users_per_session` | Max followers scanned **across all targets** before the bot stops entirely |
| `max_daily_actions` | Stops when daily action count is reached |

**Example:** 5 targets in `target.txt`, `max_users_per_session: 20` → bot scans 20 profiles total and exits, even if more targets remain.

---

## Example Scenarios

### Scenario 1: Process several brand accounts in one run

**target.txt:**
```
guiltyxapparel
brandymelvilleusa
lift_the_label
```

**config.yaml:**
```yaml
process_all: true
max_users_per_run: 10
max_users_per_session: 25
```

The bot processes up to 10 followers from each target, but stops after 25 scans total across the session.

### Scenario 2: Single target only

Set `process_all: false` in config.yaml. The bot uses the first line of `target.txt` (or `target.username` as fallback).

---

## Tips

### Comments in target.txt
Lines starting with `#` are ignored:
```
# Fashion brands
guiltyxapparel
brandymelvilleusa
```

### Check progress
- Default profile: `data/progress.json`
- With `--profile account1`: `data/progress_account1.json`

Look for `"target_profile"` to see which target was last processed.

### Terminal output
```
📋 Target queue (3): @guiltyxapparel, @brandymelvilleusa, @lift_the_label
📊 Processing profile: @guiltyxapparel
...
🛑 Session profile limit reached (max_users_per_session). Stopping bot.
```

---

## Troubleshooting

### Bot only processed one target
- Check `max_users_per_session` — it may have been reached on the first target
- Check `max_daily_actions` in config.yaml

### Bot skipped a target
- Extraction may have failed (private profile, wrong username)
- Check logs in `data/logs/bot.log`

### Username not found
- No `@` symbol in target.txt
- No trailing spaces
- Account must be public for follower extraction

---

## FAQ

**Q: Can I have multiple targets in one file?**  
A: Yes. Set `process_all: true` and put one username per line.

**Q: Will I lose progress?**  
A: No. Progress is saved after each user. Resume by running the bot again.

**Q: Can I change target.txt while the bot is running?**  
A: Changes take effect on the **next** run. Edit the file, then restart the bot.

**Q: What if target.txt is empty?**  
A: The bot falls back to `target.username` in config.yaml.
