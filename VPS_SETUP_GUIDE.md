# 🚀 VPS Setup Guide - Straddle Trading Bot

## Complete Guide to Deploy on Linux VPS

---

## 📋 Prerequisites

- ✅ Linux VPS (Ubuntu 20.04+ recommended)
- ✅ Root or sudo access
- ✅ GitHub repository uploaded (Sarabjeet101/BTC_Straddle)
- ✅ Delta Exchange API keys ready

---

## 🔧 Step 1: Connect to VPS

```bash
# SSH into your VPS
ssh root@YOUR_VPS_IP
# OR
ssh username@YOUR_VPS_IP
```

---

## 📦 Step 2: Install Required Software

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+ and pip
sudo apt install python3 python3-pip python3-venv git -y

# Verify installations
python3 --version  # Should show Python 3.9+
pip3 --version
git --version
```

---

## 📥 Step 3: Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/Sarabjeet101/BTC_Straddle.git

# Enter the directory
cd BTC_Straddle

# List files to verify
ls -la
```

**Expected files:**
```
straddle_bot.py
config.py
requirements.txt
.env (you'll create this)
test_connection.py
etc...
```

---

## 🔐 Step 4: Create .env File

```bash
# Create .env file with your API credentials
nano .env
```

**Add this content** (replace with YOUR keys):
```env
DELTA_API_KEY=Yml1AgX4au0lgMKAqFdt0ONbDgC1l1
DELTA_API_SECRET=WTxTMARtjplik4HI00Ns4q4bnuJoVicime07IhqDT6uRVdsB5AYEd3BWWS7l
TESTNET=False
```

**Save and exit:**
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter` to save

**Verify .env file:**
```bash
cat .env
```

---

## 🐍 Step 5: Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

---

## 📚 Step 6: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Verify installations
pip list
```

**Expected packages:**
- ccxt>=4.0.0
- python-dotenv>=1.0.0
- pytz>=2023.3

---

## 🧪 Step 7: Test Connection

```bash
# Test API connection
python3 test_connection.py
```

**Expected output:**
```
Testing Delta Exchange India connection...
✓ Successfully connected to Delta Exchange India!
✓ Found 1132 markets
✓ Account Balance: $47.54 USD
```

**If you see errors:**
- ❌ API Key Error → Check .env file credentials
- ❌ Network Error → Check VPS firewall/network
- ❌ IP Whitelist Error → Add VPS IP to Delta Exchange

---

## 🌐 Step 8: Get VPS IP Address (for Whitelisting)

```bash
# Get your VPS public IP
curl -s https://api.ipify.org
# OR
curl -s ifconfig.me
# OR
hostname -I
```

**Copy this IP and whitelist it in Delta Exchange:**
1. Go to https://www.india.delta.exchange/
2. Settings → API Management
3. Add VPS IP to whitelist
4. Save changes

---

## 🧪 Step 9: Test Bot Logic

```bash
# Test straddle logic without placing orders
python3 test_straddle.py
```

**Expected output:**
```
✓ Current BTC Price: $110,665.00
✓ Call Strike: $110,800 @ $398.00
✓ Put Strike: $110,400 @ $304.00
✓ All tests completed successfully!
```

---

## 🚀 Step 10: Run the Bot

### Option A: Run in Foreground (Testing)
```bash
# Run bot directly (stops when you close terminal)
python3 straddle_bot.py
```

**Output:**
```
🤖 STRADDLE BOT STARTED
Waiting for entry time: 04:00 PM IST
Press Ctrl+C to stop
```

**To stop:** Press `Ctrl + C`

---

### Option B: Run in Background (Production) ✅

```bash
# Run bot in background with nohup
nohup python3 straddle_bot.py > straddle_bot.log 2>&1 &

# Check if running
ps aux | grep straddle_bot.py

# View live logs
tail -f straddle_bot.log

# Stop following logs: Ctrl + C
```

---

### Option C: Run with Screen (Recommended) ✅✅

```bash
# Install screen
sudo apt install screen -y

# Create new screen session
screen -S straddle

# Inside screen, activate venv and run bot
source ~/BTC_Straddle/venv/bin/activate
cd ~/BTC_Straddle
python3 straddle_bot.py

# Detach from screen (bot keeps running)
# Press: Ctrl + A, then D

# Reattach to screen
screen -r straddle

# List all screens
screen -ls

# Kill screen session (stops bot)
screen -X -S straddle quit
```

---

### Option D: Run with systemd (Auto-restart) ✅✅✅

```bash
# Create systemd service file
sudo nano /etc/systemd/system/straddle-bot.service
```

**Add this content:**
```ini
[Unit]
Description=Straddle Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/BTC_Straddle
Environment="PATH=/root/BTC_Straddle/venv/bin"
ExecStart=/root/BTC_Straddle/venv/bin/python3 /root/BTC_Straddle/straddle_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save and enable:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable straddle-bot

# Start service
sudo systemctl start straddle-bot

# Check status
sudo systemctl status straddle-bot

# View logs
sudo journalctl -u straddle-bot -f

# Stop service
sudo systemctl stop straddle-bot

# Restart service
sudo systemctl restart straddle-bot
```

---

## 📊 Step 11: Monitor the Bot

### Check Logs (nohup method):
```bash
tail -f ~/BTC_Straddle/straddle_bot.log
```

### Check Logs (systemd method):
```bash
sudo journalctl -u straddle-bot -f
```

### Check if Bot is Running:
```bash
ps aux | grep straddle_bot.py
```

### Check Bot Process:
```bash
top | grep python
```

---

## 🛑 Stopping the Bot

### Foreground mode:
```bash
# Press Ctrl + C
```

### Background (nohup):
```bash
# Find process ID
ps aux | grep straddle_bot.py

# Kill process (replace PID)
kill -9 PID
```

### Screen:
```bash
screen -X -S straddle quit
```

### Systemd:
```bash
sudo systemctl stop straddle-bot
```

---

## 🔄 Updating the Bot

```bash
# Navigate to repository
cd ~/BTC_Straddle

# Stop bot first
sudo systemctl stop straddle-bot
# OR: Ctrl+C if running in foreground
# OR: screen -X -S straddle quit

# Pull latest changes
git pull origin main

# Activate venv
source venv/bin/activate

# Update dependencies (if changed)
pip install -r requirements.txt

# Restart bot
sudo systemctl start straddle-bot
# OR: python3 straddle_bot.py
```

---

## 🔍 Troubleshooting

### Bot Not Starting:
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check virtual environment
source venv/bin/activate
which python3  # Should show venv path

# Check dependencies
pip list | grep ccxt
```

### API Connection Errors:
```bash
# Test connection
python3 test_connection.py

# Check .env file
cat .env

# Verify IP whitelisted on Delta Exchange
curl -s https://api.ipify.org
```

### Permission Errors:
```bash
# Give execute permissions
chmod +x straddle_bot.py

# Check file ownership
ls -la straddle_bot.py

# Fix ownership if needed
sudo chown $USER:$USER straddle_bot.py
```

### Bot Crashes:
```bash
# Check logs
tail -50 straddle_bot.log

# Check system logs
sudo journalctl -u straddle-bot -n 50

# Check system resources
free -h  # Memory
df -h    # Disk space
```

---

## 📅 Auto-Start on Boot

### With systemd (already enabled):
```bash
sudo systemctl enable straddle-bot
```

### With crontab:
```bash
crontab -e
```

**Add this line:**
```bash
@reboot cd /root/BTC_Straddle && source venv/bin/activate && nohup python3 straddle_bot.py > straddle_bot.log 2>&1 &
```

---

## 🔐 Security Best Practices

### 1. **Secure .env File:**
```bash
# Set permissions (only owner can read)
chmod 600 .env
```

### 2. **Use SSH Keys (Not Passwords):**
```bash
# On your local machine:
ssh-keygen -t rsa -b 4096
ssh-copy-id root@YOUR_VPS_IP
```

### 3. **Enable Firewall:**
```bash
# Install UFW
sudo apt install ufw -y

# Allow SSH
sudo ufw allow ssh

# Allow HTTPS (for API)
sudo ufw allow https

# Enable firewall
sudo ufw enable
```

### 4. **Update Regularly:**
```bash
sudo apt update && sudo apt upgrade -y
```

---

## 📈 Production Checklist

Before going live:

- [ ] VPS is running and accessible
- [ ] Python 3.9+ installed
- [ ] Repository cloned
- [ ] .env file created with correct API keys
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Connection test successful (test_connection.py)
- [ ] Bot logic test successful (test_straddle.py)
- [ ] VPS IP whitelisted on Delta Exchange
- [ ] Bot runs successfully in foreground
- [ ] Bot configured to run with systemd
- [ ] Logs are accessible
- [ ] Auto-restart on crash enabled
- [ ] Auto-start on boot enabled
- [ ] .env file permissions secured (chmod 600)

---

## 🎯 Quick Command Reference

```bash
# Clone repo
git clone https://github.com/Sarabjeet101/BTC_Straddle.git
cd BTC_Straddle

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env
nano .env  # Add your API keys

# Test
python3 test_connection.py
python3 test_straddle.py

# Run (systemd - recommended)
sudo systemctl start straddle-bot
sudo systemctl status straddle-bot
sudo journalctl -u straddle-bot -f

# Run (screen - alternative)
screen -S straddle
source venv/bin/activate
python3 straddle_bot.py
# Ctrl+A, D to detach

# Monitor
tail -f straddle_bot.log
ps aux | grep straddle

# Stop
sudo systemctl stop straddle-bot
```

---

## 🆘 Support Commands

```bash
# Get VPS IP
curl -s https://api.ipify.org

# Check bot is running
ps aux | grep straddle_bot.py

# View recent logs (last 100 lines)
tail -100 straddle_bot.log

# Check system resources
htop
# OR
top

# Check disk space
df -h

# Check memory
free -h

# Test internet connectivity
ping -c 4 google.com

# Test API connectivity
curl https://api.india.delta.exchange/v2/tickers
```

---

## 📞 Need Help?

If you encounter issues:

1. **Check logs first:**
   ```bash
   tail -100 straddle_bot.log
   sudo journalctl -u straddle-bot -n 100
   ```

2. **Test connection:**
   ```bash
   python3 test_connection.py
   ```

3. **Verify credentials:**
   ```bash
   cat .env
   ```

4. **Get VPS IP:**
   ```bash
   curl -s https://api.ipify.org
   ```

---

**Good luck with your deployment! 🚀**

---

**Last Updated:** October 25, 2025
**Bot Version:** 1.0
**Python Version:** 3.9+
**OS:** Ubuntu 20.04+ (or any Linux distro)
