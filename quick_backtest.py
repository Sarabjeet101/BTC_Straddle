"""
Quick Backtest - Tests last 7 days only
Useful for quick validation without waiting for full year backtest
"""
from backtest_straddle import StraddleBacktest
from datetime import datetime, timedelta

if __name__ == "__main__":
    # Test last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print("="*60)
    print("QUICK BACKTEST - LAST 7 DAYS")
    print("="*60)
    print(f"From: {start_date.strftime('%Y-%m-%d')}")
    print(f"To: {end_date.strftime('%Y-%m-%d')}")
    print("\n⚠️  Note: Historical data availability may be limited.")
    print("Some days may be skipped if options data is not available.\n")
    
    response = input("Start quick backtest? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        backtest = StraddleBacktest(start_date, end_date)
        backtest.run_backtest()
    else:
        print("Backtest cancelled")
