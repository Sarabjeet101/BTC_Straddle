"""
Simulated Backtest with Sample Data
Shows how the strategy would perform with realistic scenarios
"""
from datetime import datetime, timedelta, time as dt_time
import random

class SimulatedBacktest:
    """Simulate straddle strategy with realistic scenarios"""
    
    def __init__(self):
        self.sl_multiplier = 1.5
        self.tp_multiplier = 0.08  # 8% remaining (92% decay)
        self.lot_size = 10
        
        # Define realistic BTC price movements
        self.scenarios = [
            {"name": "Range Bound", "movement": 0.5, "probability": 0.4},
            {"name": "Moderate Up", "movement": 2.0, "probability": 0.15},
            {"name": "Moderate Down", "movement": -2.0, "probability": 0.15},
            {"name": "Sharp Up", "movement": 4.0, "probability": 0.1},
            {"name": "Sharp Down", "movement": -4.0, "probability": 0.1},
            {"name": "Very Volatile", "movement": 6.0, "probability": 0.05},
            {"name": "Highly Range Bound", "movement": 0.2, "probability": 0.05},
        ]
    
    def simulate_day(self, day_num, scenario):
        """Simulate one trading day"""
        
        # Base BTC price around 110,000
        btc_base = 110000 + random.uniform(-5000, 5000)
        
        # OTM strikes (200 apart as typical)
        call_strike = (int(btc_base / 200) + 1) * 200
        put_strike = (int(btc_base / 200)) * 200
        
        # Typical premiums based on distance
        call_premium_entry = random.uniform(350, 500)
        put_premium_entry = random.uniform(350, 500)
        
        # Calculate SL/TP
        call_sl = call_premium_entry * self.sl_multiplier
        call_tp = call_premium_entry * self.tp_multiplier
        put_sl = put_premium_entry * self.sl_multiplier
        put_tp = put_premium_entry * self.tp_multiplier
        
        # Simulate price movement based on scenario
        btc_movement_pct = scenario["movement"]
        
        # Simulate option premium changes
        # When BTC moves up: call premium ↑, put premium ↓
        # When BTC moves down: call premium ↓, put premium ↑
        # Time decay helps both premiums ↓
        
        if abs(btc_movement_pct) > 3:  # Sharp move
            # One leg likely hits SL, other should hit TP (92% decay)
            if btc_movement_pct > 0:  # Up move
                call_exit = call_premium_entry * random.uniform(1.3, 1.6)  # Likely SL
                put_exit = put_premium_entry * random.uniform(0.03, 0.10)   # 92%+ decay - TP
                call_reason = "Stop Loss" if call_exit >= call_sl else "Time Exit"
                put_reason = "Take Profit"
            else:  # Down move
                call_exit = call_premium_entry * random.uniform(0.03, 0.10)  # 92%+ decay - TP
                put_exit = put_premium_entry * random.uniform(1.3, 1.6)     # Likely SL
                call_reason = "Take Profit"
                put_reason = "Stop Loss" if put_exit >= put_sl else "Time Exit"
        
        elif abs(btc_movement_pct) > 1.5:  # Moderate move
            # One leg may hit TP (92% decay), other stays
            if btc_movement_pct > 0:  # Up move
                call_exit = call_premium_entry * random.uniform(1.0, 1.2)
                put_exit = put_premium_entry * random.uniform(0.05, 0.15)  # Big decay
                call_reason = "Time Exit"
                put_reason = "Take Profit" if put_exit <= put_tp else "Time Exit"
            else:  # Down move
                call_exit = call_premium_entry * random.uniform(0.05, 0.15)  # Big decay
                put_exit = put_premium_entry * random.uniform(1.0, 1.2)
                call_reason = "Take Profit" if call_exit <= call_tp else "Time Exit"
                put_reason = "Time Exit"
        
        else:  # Range bound
            # Both may decay nicely toward TP
            call_exit = call_premium_entry * random.uniform(0.20, 0.50)
            put_exit = put_premium_entry * random.uniform(0.20, 0.50)
            call_reason = "Take Profit" if call_exit <= call_tp else "Time Exit"
            put_reason = "Take Profit" if put_exit <= put_tp else "Time Exit"
        
        # Calculate P&L
        call_pnl = (call_premium_entry - call_exit) * self.lot_size
        put_pnl = (put_premium_entry - put_exit) * self.lot_size
        total_pnl = call_pnl + put_pnl
        
        return {
            'day': day_num,
            'scenario': scenario["name"],
            'btc_price': btc_base,
            'btc_movement': btc_movement_pct,
            'call_strike': call_strike,
            'put_strike': put_strike,
            'call_entry': call_premium_entry,
            'call_exit': call_exit,
            'call_reason': call_reason,
            'call_pnl': call_pnl,
            'put_entry': put_premium_entry,
            'put_exit': put_exit,
            'put_reason': put_reason,
            'put_pnl': put_pnl,
            'total_pnl': total_pnl
        }
    
    def run_simulation(self, days=30):
        """Run simulation for N days"""
        
        print("\n" + "="*80)
        print("SIMULATED BACKTEST - STRADDLE STRATEGY")
        print("="*80)
        print(f"Simulation Period: {days} trading days")
        print(f"Lot Size: {self.lot_size} lots per leg")
        print(f"Entry: 4:00 PM | Exit: 5:25 PM")
        print(f"SL: {self.sl_multiplier*100}% | TP: 92% decay (to {self.tp_multiplier*100}%)")
        print("="*80)
        
        trades = []
        
        for day in range(1, days + 1):
            # Select scenario based on probability
            rand = random.random()
            cumulative = 0
            selected_scenario = self.scenarios[0]
            
            for scenario in self.scenarios:
                cumulative += scenario["probability"]
                if rand <= cumulative:
                    selected_scenario = scenario
                    break
            
            trade = self.simulate_day(day, selected_scenario)
            trades.append(trade)
            
            # Print trade details
            result = "✅ WIN" if trade['total_pnl'] > 0 else "❌ LOSS"
            print(f"\nDay {day:2d} | {trade['scenario']:<20} | "
                  f"BTC: ${trade['btc_price']:>8,.0f} ({trade['btc_movement']:+.1f}%) | "
                  f"P&L: ${trade['total_pnl']:>8.2f} {result}")
            print(f"       Call: ${trade['call_entry']:.0f} → ${trade['call_exit']:.0f} "
                  f"({trade['call_reason']}) = ${trade['call_pnl']:+.2f}")
            print(f"       Put:  ${trade['put_entry']:.0f} → ${trade['put_exit']:.0f} "
                  f"({trade['put_reason']}) = ${trade['put_pnl']:+.2f}")
        
        # Print summary
        self.print_summary(trades)
    
    def print_summary(self, trades):
        """Print simulation summary"""
        
        print("\n\n" + "="*80)
        print("SIMULATION SUMMARY")
        print("="*80)
        
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t['total_pnl'] > 0])
        losing_trades = len([t for t in trades if t['total_pnl'] < 0])
        
        total_pnl = sum([t['total_pnl'] for t in trades])
        avg_pnl = total_pnl / total_trades
        max_profit = max([t['total_pnl'] for t in trades])
        max_loss = min([t['total_pnl'] for t in trades])
        
        win_rate = (winning_trades / total_trades * 100)
        
        print(f"\n📊 Performance Metrics:")
        print(f"   Total Trades: {total_trades}")
        print(f"   Winning Trades: {winning_trades} ({win_rate:.1f}%)")
        print(f"   Losing Trades: {losing_trades} ({100-win_rate:.1f}%)")
        
        print(f"\n💰 P&L Summary:")
        print(f"   Total P&L: ${total_pnl:+,.2f}")
        print(f"   Average P&L per Trade: ${avg_pnl:+.2f}")
        print(f"   Best Trade: ${max_profit:+.2f}")
        print(f"   Worst Trade: ${max_loss:+.2f}")
        
        # Winning vs Losing stats
        if winning_trades > 0:
            avg_win = sum([t['total_pnl'] for t in trades if t['total_pnl'] > 0]) / winning_trades
            print(f"   Average Win: ${avg_win:+.2f}")
        
        if losing_trades > 0:
            avg_loss = sum([t['total_pnl'] for t in trades if t['total_pnl'] < 0]) / losing_trades
            print(f"   Average Loss: ${avg_loss:+.2f}")
        
        # Exit reason breakdown
        call_sl = len([t for t in trades if t['call_reason'] == 'Stop Loss'])
        call_tp = len([t for t in trades if t['call_reason'] == 'Take Profit'])
        call_time = len([t for t in trades if t['call_reason'] == 'Time Exit'])
        
        put_sl = len([t for t in trades if t['put_reason'] == 'Stop Loss'])
        put_tp = len([t for t in trades if t['put_reason'] == 'Take Profit'])
        put_time = len([t for t in trades if t['put_reason'] == 'Time Exit'])
        
        print(f"\n🎯 Exit Breakdown:")
        print(f"   Call Options:")
        print(f"      Stop Loss: {call_sl} ({call_sl/total_trades*100:.1f}%)")
        print(f"      Take Profit: {call_tp} ({call_tp/total_trades*100:.1f}%)")
        print(f"      Time Exit: {call_time} ({call_time/total_trades*100:.1f}%)")
        print(f"   Put Options:")
        print(f"      Stop Loss: {put_sl} ({put_sl/total_trades*100:.1f}%)")
        print(f"      Take Profit: {put_tp} ({put_tp/total_trades*100:.1f}%)")
        print(f"      Time Exit: {put_time} ({put_time/total_trades*100:.1f}%)")
        
        # Scenario breakdown
        print(f"\n📈 Scenario Breakdown:")
        for scenario in self.scenarios:
            scenario_trades = [t for t in trades if t['scenario'] == scenario['name']]
            if scenario_trades:
                count = len(scenario_trades)
                wins = len([t for t in scenario_trades if t['total_pnl'] > 0])
                avg_pnl_scenario = sum([t['total_pnl'] for t in scenario_trades]) / count
                print(f"   {scenario['name']:<20}: {count:2d} trades | "
                      f"{wins:2d} wins ({wins/count*100:5.1f}%) | "
                      f"Avg P&L: ${avg_pnl_scenario:+8.2f}")
        
        print("\n" + "="*80)
        
        if total_pnl > 0:
            print(f"✅ Strategy would be PROFITABLE over {total_trades} days: ${total_pnl:+,.2f}")
        else:
            print(f"❌ Strategy would show LOSS over {total_trades} days: ${total_pnl:+,.2f}")
        
        print("="*80)
        
        print("\n⚠️  DISCLAIMER: This is a SIMULATION with realistic scenarios.")
        print("Actual results will vary based on real market conditions.")
        print("Past simulated performance does not guarantee future results.")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("STRADDLE STRATEGY - SIMULATED BACKTEST")
    print("="*80)
    print("\n⚠️  Since historical options data is not available from the API,")
    print("this simulation uses realistic scenarios based on typical BTC movements.\n")
    
    days = input("How many trading days to simulate? (default 30): ")
    
    try:
        days = int(days) if days else 30
    except:
        days = 30
    
    random.seed(42)  # For reproducibility
    sim = SimulatedBacktest()
    sim.run_simulation(days)
