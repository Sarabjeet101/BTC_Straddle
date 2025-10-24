# BTCUSD Straddle Trading Bot

Automated options straddle strategy for Delta Exchange India.

## Strategy Overview

**Type**: Short Straddle (Sell 1 strike OTM on both Call and Put)

**Underlying**: BTCUSD Options

**Entry Time**: 4:00 PM IST

**Exit Time**: 5:25 PM IST

**Stop Loss**: 150% of entry premium

**Take Profit**: 92% of entry premium

## How It Works

1. **At 4:30 PM IST**, the bot:
   - Fetches current BTC/USD price
   - Finds the nearest 1 strike OTM call option (strike above current price)
   - Finds the nearest 1 strike OTM put option (strike below current price)
   - Sells both options (short straddle)

2. **During the trade**, the bot:
   - Monitors both positions continuously
   - Checks if Stop Loss is hit (premium reaches 150% of entry)
   - Checks if Take Profit is hit (premium drops to 92% of entry)
   - Closes individual legs if SL/TP is triggered

3. **At 5:25 PM IST**, the bot:
   - Closes all remaining open positions
   - Calculates P&L for the day

## Example Trade

```
Current BTC Price: $110,526
Call Strike: $110,600 (1 strike OTM above)
Put Strike: $110,400 (1 strike OTM below)

Lot Size: 10 lots (0.01 BTC per leg)

Entry:
- Sell Call @ $451 × 10 lots = $4,510 → SL: $676.50 | TP: $414.92
- Sell Put @ $377 × 10 lots = $3,770 → SL: $565.50 | TP: $346.84
- Total Premium Collected: $8,280

Scenarios:
✅ If both premiums decay below TP → Profit ~$650
✅ If market stays range-bound → Close at exit time with profit
⚠️ If BTC moves sharply → SL triggers on one leg, other may offset
```

## Files

- `straddle_bot.py` - Main trading bot (sells 10 lots per leg)
- `test_straddle.py` - Test script (no real orders)
- `backtest_straddle.py` - Backtest from Jan 1, 2025 to current date
- `config.py` - Configuration settings
- `.env` - API credentials

## Usage

### Test Mode (Recommended First)

```bash
python test_straddle.py
```

This will:
- Test all bot functions
- Show you the strikes it would select
- Display premiums and SL/TP levels for 10 lots
- **NOT place any actual orders**

### Backtest the Strategy

```bash
python backtest_straddle.py
```

This will:
- Simulate trades from January 1, 2025 to current date
- Show historical performance
- Display win rate, total P&L, and trade details
- **Does NOT place real orders** (uses historical data)

**Note**: Backtesting requires historical data availability from Delta Exchange. Some days may be skipped if data is not available.

### Live Trading

```bash
python straddle_bot.py
```

This will:
- Start the bot
- Wait for 4:30 PM IST
- Automatically enter the straddle
- Monitor positions
- Exit at 5:25 PM IST

### To Stop the Bot

Press `Ctrl+C` - The bot will safely close all open positions before stopping.

## Important Settings

### Production vs Testnet

In `config.py`, line 23:
```python
TESTNET = False  # Currently set to PRODUCTION
```

⚠️ **WARNING**: Currently running in PRODUCTION mode with REAL money!

To test safely, set:
```python
TESTNET = True
```

### Modify Strategy Parameters

In `straddle_bot.py`, you can adjust:

```python
# Line 41-42: Stop Loss and Take Profit
self.sl_multiplier = 1.5   # 150% of premium
self.tp_multiplier = 0.92  # 92% of premium

# Line 45-46: Entry and Exit Times
self.entry_time = dt_time(16, 30)  # 4:30 PM
self.exit_time = dt_time(17, 25)   # 5:25 PM

# Line 183-184: Order quantity
quantity = 1  # Number of contracts
```

## Risk Management

### Position Sizing
- Default: **10 lots per option** (0.01 BTC total)
- 1 BTC = 1000 lots on Delta Exchange India
- Adjust based on your account size
- Current setup requires ~$8,000-10,000 in premium collection

### Stop Loss Logic
- Each leg has independent SL at 150% of entry premium
- SL triggers automatically close that specific leg
- Other leg continues until TP/exit time

### Maximum Loss Scenarios
1. **Both legs hit SL**: Loss = 50% of total premium collected per leg
2. **Sharp directional move**: One leg hits SL (~50% loss), other gains
3. **Extreme volatility**: Both legs may hit SL

### Daily P&L
The bot shows P&L when closing positions:
```
Entry: $412.00 | Exit: $380.00 | P&L: $32.00
```

## Monitoring

The bot prints status updates:
- Entry confirmation with strikes and premiums
- SL/TP levels for each leg
- Position monitoring every 30 seconds
- SL/TP triggers
- Exit confirmation with P&L

## Troubleshooting

### "No options found"
- Check if market is open
- Verify BTC options are available on Delta Exchange India
- May need to wait for options to be listed

### "Failed to get BTC price"
- Check internet connection
- Verify API credentials
- Check Delta Exchange India status

### "Error placing order"
- Insufficient balance
- API key permissions (need trading enabled)
- Market closed or suspended

### Wrong entry time
- Bot uses IST (Indian Standard Time)
- System timezone doesn't matter - bot handles conversion

## Safety Features

✅ Automatic position closure on exit time
✅ Independent SL/TP per leg
✅ Graceful shutdown (Ctrl+C closes positions)
✅ Rate limiting enabled
✅ Error handling and logging

## Recommended Workflow

1. **First Time Setup**:
   ```bash
   python test_connection.py  # Verify API works
   python test_straddle.py    # Test bot logic
   ```

2. **Before Live Trading**:
   - Verify you have sufficient balance
   - Understand the risks
   - Start with 1 contract
   - Monitor the first few trades manually

3. **Live Trading**:
   ```bash
   python straddle_bot.py
   ```

4. **Review**:
   - Keep track of daily P&L
   - Analyze which scenarios work best
   - Adjust parameters based on results

## Support

- Check Delta Exchange India documentation for options trading
- Verify option symbols format: `BTC/USD:USD-YYMMDD-STRIKE-C/P`
- Test during market hours (IST business hours)

---

**Disclaimer**: This bot trades real money. Use at your own risk. Always test thoroughly before live trading. Past performance doesn't guarantee future results.
