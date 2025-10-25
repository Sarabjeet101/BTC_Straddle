"""
Analyze ETH backtest data and validate against our strategy
"""
import csv
from datetime import datetime

print("="*70)
print("ETH STRADDLE BACKTEST ANALYSIS")
print("="*70)

# Read CSV file
trades = []
with open('68fcae708e3a87a7ae16ded9_1761390195.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        trades.append(row)

# Filter main trade rows (not sub-legs)
main_trades = [t for t in trades if '.' not in t['Index']]
call_legs = [t for t in trades if t['Instrument-Kind'] == 'CE']
put_legs = [t for t in trades if t['Instrument-Kind'] == 'PE']

print(f"\n📊 BACKTEST CONFIGURATION")
print(f"   Asset: ETH/USD")
print(f"   Entry Time: 1:30 PM (13:30)")
print(f"   Exit Time: 5:25 PM (17:25)")
print(f"   Strategy: Short Straddle (1 OTM)")
print(f"   Quantity: 0.1 ETH per leg (10 lots)")
print(f"   SL/TP: Time-based exit only")

# Overall statistics
total_trades = len(main_trades)
winning_trades = len([t for t in main_trades if float(t['P/L']) > 0])
losing_trades = len([t for t in main_trades if float(t['P/L']) < 0])
breakeven_trades = len([t for t in main_trades if float(t['P/L']) == 0])

total_pnl = sum([float(t['P/L']) for t in main_trades])
avg_pnl = total_pnl / total_trades if total_trades > 0 else 0

wins_pnl = [float(t['P/L']) for t in main_trades if float(t['P/L']) > 0]
losses_pnl = [float(t['P/L']) for t in main_trades if float(t['P/L']) < 0]

avg_win = sum(wins_pnl) / len(wins_pnl) if wins_pnl else 0
avg_loss = sum(losses_pnl) / len(losses_pnl) if losses_pnl else 0

best_trade = max([float(t['P/L']) for t in main_trades])
worst_trade = min([float(t['P/L']) for t in main_trades])

win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

print(f"\n📈 OVERALL PERFORMANCE")
print(f"   Total Trades: {total_trades}")
print(f"   Period: Jan 1 - Oct (10 months)")
print(f"   Total P&L: ${total_pnl:,.2f}")
print(f"   Average P&L per Trade: ${avg_pnl:.2f}")

print(f"\n🎯 WIN/LOSS STATISTICS")
print(f"   Winning Trades: {winning_trades} ({win_rate:.1f}%)")
print(f"   Losing Trades: {losing_trades} ({(losing_trades/total_trades*100):.1f}%)")
print(f"   Breakeven Trades: {breakeven_trades}")
print(f"   Win Rate: {win_rate:.2f}%")

print(f"\n💰 PROFIT/LOSS DETAILS")
print(f"   Average Win: ${avg_win:.2f}")
print(f"   Average Loss: ${avg_loss:.2f}")
print(f"   Best Trade: ${best_trade:.2f}")
print(f"   Worst Trade: ${worst_trade:.2f}")
if losses_pnl:
    pf = abs(sum(wins_pnl) / sum(losses_pnl))
    print(f"   Profit Factor: {pf:.2f}")

# Leg analysis
call_wins = len([t for t in call_legs if float(t['P/L']) > 0])
put_wins = len([t for t in put_legs if float(t['P/L']) > 0])

call_total_pnl = sum([float(t['P/L']) for t in call_legs])
put_total_pnl = sum([float(t['P/L']) for t in put_legs])

print(f"\n📊 LEG-BY-LEG ANALYSIS")
print(f"   CALL Options (CE):")
print(f"      Total Legs: {len(call_legs)}")
print(f"      Winning Legs: {call_wins} ({call_wins/len(call_legs)*100:.1f}%)")
print(f"      Total P&L: ${call_total_pnl:,.2f}")
print(f"      Avg P&L: ${call_total_pnl/len(call_legs):.2f}")

print(f"\n   PUT Options (PE):")
print(f"      Total Legs: {len(put_legs)}")
print(f"      Winning Legs: {put_wins} ({put_wins/len(put_legs)*100:.1f}%)")
print(f"      Total P&L: ${put_total_pnl:,.2f}")
print(f"      Avg P&L: ${put_total_pnl/len(put_legs):.2f}")

# Monthly breakdown
monthly_pnl = {}
for trade in main_trades:
    date = datetime.strptime(trade['Entry-Date'], '%Y-%m-%d')
    month_key = date.strftime('%Y-%m')
    if month_key not in monthly_pnl:
        monthly_pnl[month_key] = {'pnl': 0, 'trades': 0, 'wins': 0}
    monthly_pnl[month_key]['pnl'] += float(trade['P/L'])
    monthly_pnl[month_key]['trades'] += 1
    if float(trade['P/L']) > 0:
        monthly_pnl[month_key]['wins'] += 1

print(f"\n📅 MONTHLY BREAKDOWN")
print(f"{'Month':<12} {'Trades':<8} {'Win Rate':<10} {'P&L':<12} {'Avg/Day':<10}")
print("-" * 70)
for month in sorted(monthly_pnl.keys()):
    data = monthly_pnl[month]
    wr = (data['wins'] / data['trades'] * 100) if data['trades'] > 0 else 0
    avg = data['pnl'] / data['trades'] if data['trades'] > 0 else 0
    month_name = datetime.strptime(month, '%Y-%m').strftime('%b %Y')
    print(f"{month_name:<12} {data['trades']:<8} {wr:>6.1f}%    ${data['pnl']:>8.2f}   ${avg:>7.2f}")

# Risk metrics
max_consecutive_losses = 0
current_streak = 0
for trade in main_trades:
    if float(trade['P/L']) < 0:
        current_streak += 1
        max_consecutive_losses = max(max_consecutive_losses, current_streak)
    else:
        current_streak = 0

# Calculate drawdown
cumulative_pnl = 0
peak = 0
max_drawdown = 0
for trade in main_trades:
    cumulative_pnl += float(trade['P/L'])
    if cumulative_pnl > peak:
        peak = cumulative_pnl
    drawdown = peak - cumulative_pnl
    if drawdown > max_drawdown:
        max_drawdown = drawdown

print(f"\n⚠️  RISK METRICS")
print(f"   Max Consecutive Losses: {max_consecutive_losses}")
print(f"   Max Drawdown: ${max_drawdown:.2f}")

# Strategy validation
print(f"\n" + "="*70)
print(f"✅ STRATEGY VALIDATION")
print(f"="*70)

# Check entry time
sample_entries = set([t['Entry-Time'] for t in main_trades[:10]])
print(f"   Entry Time Check: {sample_entries}")
if '13:30:00' in sample_entries:
    print(f"   ✅ Entry time matches: 1:30 PM (13:30)")
else:
    print(f"   ❌ Entry time mismatch!")

# Check exit time
sample_exits = set([t['ExitTime'] for t in main_trades[:10]])
print(f"   Exit Time Check: {sample_exits}")
if '17:25:00' in sample_exits:
    print(f"   ✅ Exit time matches: 5:25 PM (17:25)")
else:
    print(f"   ❌ Exit time mismatch!")

# Check quantity
quantities = set([t['Quantity'] for t in call_legs[:5]])
print(f"   Quantity Check: {quantities}")
if '0.1' in quantities:
    print(f"   ✅ Quantity matches: 0.1 ETH (10 lots)")
else:
    print(f"   ❌ Quantity mismatch!")

# Check position type
positions = set([t['Position'] for t in call_legs[:5]])
print(f"   Position Type Check: {positions}")
if 'Sell' in positions:
    print(f"   ✅ Position type matches: Sell (Short)")
else:
    print(f"   ❌ Position type mismatch!")

print(f"\n" + "="*70)
print(f"💵 PROJECTED ANNUAL PERFORMANCE")
print(f"="*70)
months_traded = len(monthly_pnl)
monthly_avg = total_pnl / months_traded if months_traded > 0 else 0
annual_projection = monthly_avg * 12

print(f"   Months Traded: {months_traded}")
print(f"   Average per Month: ${monthly_avg:.2f}")
print(f"   Annual Projection: ${annual_projection:,.2f}")
print(f"   Daily Average: ${avg_pnl:.2f}")

print(f"\n" + "="*70)
print(f"🎯 COMPARISON WITH BTC BACKTEST")
print(f"="*70)
print(f"   BTC Backtest (10 months): $8,325.84")
print(f"   ETH Backtest (10 months): ${total_pnl:.2f}")
print(f"   Difference: ${total_pnl - 8325.84:.2f}")
print(f"   ETH vs BTC: {(total_pnl / 8325.84 - 1) * 100:+.1f}%")

print(f"\n" + "="*70)
print(f"✓ Analysis Complete!")
print(f"="*70)
