# 🖥️ Screen Commands - Quick Reference

## Switching to Your Bot Screen

### **List All Screen Sessions:**
```bash
screen -ls
```

### **Reattach to Your Bot Screen:**
```bash
# If screen is named "straddle"
screen -r straddle

# OR if only one screen exists
screen -r
```

### **Force Reattach (if already attached elsewhere):**
```bash
screen -d -r straddle
```

---

## Common Screen Commands

| Action | Command |
|--------|---------|
| **List screens** | `screen -ls` |
| **Attach to screen** | `screen -r straddle` |
| **Force attach** | `screen -d -r straddle` |
| **Create new screen** | `screen -S straddle` |
| **Detach from screen** | `Ctrl+A` then `D` |
| **Kill screen** | `screen -X -S straddle quit` |
| **Scroll up in screen** | `Ctrl+A` then `Esc`, use arrows |
| **Exit scroll mode** | Press `Esc` |

---

## Starting Bot in Screen

```bash
# 1. SSH into VPS
ssh root@YOUR_VPS_IP

# 2. Create screen session
screen -S straddle

# 3. Navigate and activate environment
cd ~/BTC_Straddle
source venv/bin/activate

# 4. Run bot
python3 straddle_bot.py

# 5. Detach (bot keeps running)
# Press: Ctrl+A, then D
```

---

## Checking Bot Status

```bash
# Check if screen is running
screen -ls

# Check if bot process is running
ps aux | grep straddle_bot.py

# View logs (if using nohup)
tail -f ~/BTC_Straddle/straddle_bot.log
```

---

## Troubleshooting

### No screens found:
```bash
# Bot not running, start new screen
screen -S straddle
cd ~/BTC_Straddle
source venv/bin/activate
python3 straddle_bot.py
```

### Screen says "Attached":
```bash
# Someone else viewing or terminal crashed
# Force reattach:
screen -d -r straddle
```

### Can't install screen:
```bash
sudo apt update
sudo apt install screen -y
```

---

**Quick Access:** After SSH login, just type `screen -r straddle` to view your bot! 🚀
