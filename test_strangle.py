"""
Test Strangle Bot - Find options closest to $50 premium
"""
import ccxt
from config import Config

print("="*70)
print("STRANGLE BOT TEST - Finding Options Closest to $50")
print("="*70)

# Validate configuration
Config.validate()

# Initialize exchange
exchange = ccxt.delta({
    'apiKey': Config.DELTA_API_KEY,
    'secret': Config.DELTA_API_SECRET,
    'enableRateLimit': True,
    'urls': {
        'api': {
            'public': 'https://api.india.delta.exchange',
            'private': 'https://api.india.delta.exchange',
        }
    },
})

print("\n✓ Running in PRODUCTION mode")
print("Loading markets...")
markets = exchange.load_markets()
print(f"✓ Loaded {len(markets)} markets")

# Get current BTC price
print("\nFetching BTC price...")
ticker = exchange.fetch_ticker('BTC/USD:USD')
btc_price = ticker['last']
print(f"✓ Current BTC Price: ${btc_price:,.2f}")

# Get all BTC options
print("\nFinding BTC options...")
options = []
for symbol, market in markets.items():
    if 'BTC/USD:USD' in symbol and ('-C' in symbol or '-P' in symbol):
        parts = symbol.split('-')
        if len(parts) >= 4:
            try:
                strike = float(parts[-2])
                expiry = parts[1]
                opt_type = 'call' if '-C' in symbol else 'put'
                options.append({
                    'symbol': symbol,
                    'strike': strike,
                    'expiry': expiry,
                    'type': opt_type
                })
            except:
                pass

print(f"✓ Found {len(options)} BTC options")

# Get today's expiry
expiries = sorted(set([opt['expiry'] for opt in options]))
today_expiry = expiries[0]
print(f"\n📅 Using expiry: {today_expiry}")

# Filter for today's expiry
calls = [opt for opt in options if opt['type'] == 'call' and opt['expiry'] == today_expiry]
puts = [opt for opt in options if opt['type'] == 'put' and opt['expiry'] == today_expiry]

print(f"   Calls available: {len(calls)}")
print(f"   Puts available: {len(puts)}")

# Find call closest to $50
target_premium = 50
print(f"\n🔍 Searching for options closest to ${target_premium}...")

best_call = None
min_call_diff = float('inf')

print("\nScanning Call options...")
for i, call in enumerate(calls[:50]):  # Limit to 50 to avoid rate limits
    try:
        call_ticker = exchange.fetch_ticker(call['symbol'])
        premium = call_ticker['last']
        
        if premium:
            diff = abs(premium - target_premium)
            if diff < min_call_diff:
                min_call_diff = diff
                best_call = {
                    'symbol': call['symbol'],
                    'strike': call['strike'],
                    'premium': premium
                }
            
            # Print promising candidates
            if abs(premium - target_premium) < 20:
                print(f"   Strike ${call['strike']:,.0f}: ${premium:.2f} (diff: ${diff:.2f})")
        
        if (i + 1) % 10 == 0:
            print(f"   ... scanned {i + 1} calls")
            
    except Exception as e:
        pass

# Find put closest to $50
best_put = None
min_put_diff = float('inf')

print("\nScanning Put options...")
for i, put in enumerate(puts[:50]):  # Limit to 50 to avoid rate limits
    try:
        put_ticker = exchange.fetch_ticker(put['symbol'])
        premium = put_ticker['last']
        
        if premium:
            diff = abs(premium - target_premium)
            if diff < min_put_diff:
                min_put_diff = diff
                best_put = {
                    'symbol': put['symbol'],
                    'strike': put['strike'],
                    'premium': premium
                }
            
            # Print promising candidates
            if abs(premium - target_premium) < 20:
                print(f"   Strike ${put['strike']:,.0f}: ${premium:.2f} (diff: ${diff:.2f})")
        
        if (i + 1) % 10 == 0:
            print(f"   ... scanned {i + 1} puts")
            
    except Exception as e:
        pass

# Results
print("\n" + "="*70)
print("🎯 SELECTED OPTIONS")
print("="*70)

if best_call:
    print(f"\n📞 CALL Option:")
    print(f"   Symbol: {best_call['symbol']}")
    print(f"   Strike: ${best_call['strike']:,.0f}")
    print(f"   Premium: ${best_call['premium']:.2f}")
    print(f"   Difference from target: ${abs(best_call['premium'] - target_premium):.2f}")
else:
    print("\n❌ No suitable call found")

if best_put:
    print(f"\n📉 PUT Option:")
    print(f"   Symbol: {best_put['symbol']}")
    print(f"   Strike: ${best_put['strike']:,.0f}")
    print(f"   Premium: ${best_put['premium']:.2f}")
    print(f"   Difference from target: ${abs(best_put['premium'] - target_premium):.2f}")
else:
    print("\n❌ No suitable put found")

if best_call and best_put:
    # Combined premium is just the sum of the two option premiums
    combined_premium = best_call['premium'] + best_put['premium']
    lot_size = 5  # 5 lots = 0.005 BTC
    
    sl_multiplier = 3.0  # 200% increase = 3x entry
    sl_level = combined_premium * sl_multiplier
    
    print("\n" + "="*70)
    print("💰 COMBINED STRANGLE")
    print("="*70)
    print(f"   Combined Entry Premium: ${combined_premium:.2f}")
    print(f"      (Call ${best_call['premium']:.2f} + Put ${best_put['premium']:.2f})")
    print(f"\n   Lot Size: {lot_size} lots (0.005 BTC)")
    print(f"   Total Premium Collected: ${combined_premium * lot_size:.2f}")
    
    print(f"\n   Stop Loss Level (300%): ${sl_level:.2f}")
    print(f"   SL triggers if combined premium ≥ ${sl_level:.2f}")
    
    print(f"\n   Best Case (both decay to $0):")
    print(f"      Profit per option: ${combined_premium:.2f}")
    print(f"      Total Profit ({lot_size} lots): ${combined_premium * lot_size:.2f}")
    
    print(f"\n   Worst Case (SL hit at 200%):")
    print(f"      Loss per option: ${sl_level - combined_premium:.2f}")
    print(f"      Total Loss ({lot_size} lots): ${(sl_level - combined_premium) * lot_size:.2f}")
    
    print(f"\n   Risk-Reward Ratio: 1:1 (profit ${combined_premium:.2f} vs loss ${sl_level - combined_premium:.2f})")

print("\n" + "="*70)
print("✓ Test Complete!")
print("="*70)
