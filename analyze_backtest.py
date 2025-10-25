"""
Analyze real backtest data from CSV
"""
import csv
from datetime import datetime

# Read CSV file
trades = []
with open('BTC Trades v2.csv', 'r') as f:
    reader = csv.reader(f)
    headers = next(reader)  # Skip header
    for row in reader:
        if len(row) >= 12:
            trades.append({
                'Index': row[0],
                'Entry Date': row[1],
                'Entry Time': row[2],
                'Exit Date': row[3],
                'Exit Time': row[4],
                'Type': row[5],
                'Strike': row[6],
                'B/S': row[7],
                'Qty': row[8],
                'Entry Price': row[9],
                'Exit Price': row[10],
                'P/L': row[11]
            })

# Filter main trade rows (not sub-legs)
main_trades = [t for t in trades if '.' not in str(t['Index'])]

print("="*70)
print("REAL BACKTEST ANALYSIS - January to October 2025")
print("="*70)

# Calculate statistics
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

print(f"\n📊 OVERALL PERFORMANCE")
print(f"   Total Trades: {total_trades}")
print(f"   Period: Jan 1, 2025 - Oct 24, 2025 ({total_trades} trading days)")
print(f"   Total P&L: ${total_pnl:,.2f}")
print(f"   Average P&L per Trade: ${avg_pnl:.2f}")

print(f"\n📈 WIN/LOSS STATISTICS")
print(f"   Winning Trades: {winning_trades} ({win_rate:.1f}%)")
print(f"   Losing Trades: {losing_trades} ({(losing_trades/total_trades*100):.1f}%)")
print(f"   Breakeven Trades: {breakeven_trades}")
print(f"   Win Rate: {win_rate:.2f}%")

print(f"\n💰 PROFIT/LOSS DETAILS")
print(f"   Average Win: ${avg_win:.2f}")
print(f"   Average Loss: ${avg_loss:.2f}")
print(f"   Best Trade: ${best_trade:.2f}")
print(f"   Worst Trade: ${worst_trade:.2f}")
print(f"   Profit Factor: {abs(sum(wins_pnl) / sum(losses_pnl)):.2f}" if losses_pnl else "N/A")

# Monthly breakdown
monthly_pnl = {}
for trade in main_trades:
    date = datetime.strptime(trade['Entry Date'], '%Y-%m-%d')
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

# Analyze trade legs
print(f"\n📊 LEG-BY-LEG ANALYSIS")
call_legs = [t for t in trades if t['Type'] == 'CE']
put_legs = [t for t in trades if t['Type'] == 'PE']

call_wins = len([t for t in call_legs if float(t['P/L']) > 0])
put_wins = len([t for t in put_legs if float(t['P/L']) > 0])

call_total_pnl = sum([float(t['P/L']) for t in call_legs])
put_total_pnl = sum([float(t['P/L']) for t in put_legs])

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

# Risk metrics
print(f"\n⚠️  RISK METRICS")
consecutive_losses = 0
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

print(f"   Max Consecutive Losses: {max_consecutive_losses}")
print(f"   Max Drawdown: ${max_drawdown:.2f}")

# Scaling to 10 lots
print(f"\n" + "="*70)
print(f"💵 SCALED TO 10 LOTS (Current backtest is 0.01 BTC = 10 lots)")
print(f"="*70)
print(f"   Total P&L: ${total_pnl * 10:,.2f}")
print(f"   Avg P&L per Trade: ${avg_pnl * 10:.2f}")
print(f"   Best Trade: ${best_trade * 10:.2f}")
print(f"   Worst Trade: ${worst_trade * 10:.2f}")
print(f"   Monthly Avg: ${(total_pnl / 10) * 10:,.2f}")

print(f"\n" + "="*70)
print(f"✓ Analysis Complete!")
print(f"="*70)
