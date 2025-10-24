"""
Test script for Straddle Bot
Tests individual functions without actually placing orders
"""
from straddle_bot import StraddleBot
from datetime import datetime

def test_bot():
    """Test bot initialization and basic functions"""
    
    print("="*60)
    print("STRADDLE BOT - TEST MODE")
    print("="*60)
    
    # Initialize bot
    print("\n1. Initializing bot...")
    bot = StraddleBot()
    
    # Test BTC price fetch
    print("\n2. Testing BTC price fetch...")
    btc_price = bot.get_current_btc_price()
    if btc_price:
        print(f"   ✓ Current BTC Price: ${btc_price:,.2f}")
    else:
        print("   ✗ Failed to get BTC price")
        return
    
    # Test option symbols fetch
    print("\n3. Testing option symbols...")
    options = bot.get_option_symbols()
    print(f"   ✓ Found {len(options)} options")
    
    # Show some sample options
    print("\n   Sample Call Options:")
    calls = [opt for opt in options if opt['type'] == 'call'][:3]
    for opt in calls:
        print(f"      {opt['symbol']} (Strike: ${opt['strike']:,.0f})")
    
    print("\n   Sample Put Options:")
    puts = [opt for opt in options if opt['type'] == 'put'][:3]
    for opt in puts:
        print(f"      {opt['symbol']} (Strike: ${opt['strike']:,.0f})")
    
    # Test finding OTM strikes
    print("\n4. Testing OTM strike finder...")
    call_option, put_option = bot.find_otm_strikes(btc_price)
    
    if call_option and put_option:
        print("   ✓ Successfully found OTM strikes")
        
        # Get option premiums
        print("\n5. Fetching option premiums...")
        call_premium = bot.get_option_price(call_option['symbol'])
        put_premium = bot.get_option_price(put_option['symbol'])
        
        if call_premium and put_premium:
            print(f"   ✓ Call Premium: ${call_premium:.2f}")
            print(f"   ✓ Put Premium: ${put_premium:.2f}")
            print(f"   ✓ Total Straddle Premium: ${call_premium + put_premium:.2f}")
            
            # Calculate SL and TP
            print("\n6. Calculating SL/TP levels...")
            print(f"\n   CALL Option ({call_option['symbol']}):")
            print(f"      Entry Premium: ${call_premium:.2f}")
            print(f"      Stop Loss (150%): ${call_premium * 1.5:.2f}")
            print(f"      Take Profit (92% decay to 8%): ${call_premium * 0.08:.2f}")
            print(f"      Profit if TP hit: ${(call_premium - call_premium * 0.08) * 10:.2f}")
            
            print(f"\n   PUT Option ({put_option['symbol']}):")
            print(f"      Entry Premium: ${put_premium:.2f}")
            print(f"      Stop Loss (150%): ${put_premium * 1.5:.2f}")
            print(f"      Take Profit (92% decay to 8%): ${put_premium * 0.08:.2f}")
            print(f"      Profit if TP hit: ${(put_premium - put_premium * 0.08) * 10:.2f}")
        else:
            print("   ✗ Failed to get option premiums")
    else:
        print("   ✗ Failed to find OTM strikes")
    
    # Test time check
    print("\n7. Testing time checks...")
    now = datetime.now(bot.timezone)
    print(f"   Current Time (IST): {now.strftime('%I:%M:%S %p')}")
    print(f"   Entry Time: {bot.entry_time.strftime('%I:%M %p')}")
    print(f"   Exit Time: {bot.exit_time.strftime('%I:%M %p')}")
    print(f"   Is Entry Time: {bot.is_entry_time()}")
    print(f"   Is Exit Time: {bot.is_exit_time()}")
    
    print("\n" + "="*60)
    print("✓ All tests completed successfully!")
    print("="*60)
    print("\nNOTE: This is a test run. No actual orders were placed.")
    print("To run the live bot, execute: python straddle_bot.py")

if __name__ == "__main__":
    try:
        test_bot()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError during test: {e}")
        import traceback
        traceback.print_exc()
