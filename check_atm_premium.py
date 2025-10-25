"""
Quick script to fetch ATM strike premiums
"""
import ccxt
from config import Config

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

print("="*60)
print("ATM STRIKE PREMIUM CHECK")
print("="*60)

# Load markets
print("\nLoading markets...")
markets = exchange.load_markets()
print(f"✓ Loaded {len(markets)} markets")

# Get current BTC price
print("\nFetching BTC price...")
ticker = exchange.fetch_ticker('BTC/USD:USD')
btc_price = ticker['last']
print(f"✓ Current BTC Price: ${btc_price:,.2f}")

# Get all options
print("\nFinding options...")
options = []
for symbol, market in markets.items():
    if 'BTC/USD:USD' in symbol and ('-C' in symbol or '-P' in symbol):
        # Extract strike and expiry
        parts = symbol.split('-')
        if len(parts) >= 4:
            try:
                strike = float(parts[-2])
                expiry = parts[1]
                opt_type = 'Call' if '-C' in symbol else 'Put'
                options.append({
                    'symbol': symbol,
                    'strike': strike,
                    'expiry': expiry,
                    'type': opt_type
                })
            except:
                pass

# Get today's expiry (nearest expiry)
expiries = sorted(set([opt['expiry'] for opt in options]))
if not expiries:
    print("❌ No options found!")
    exit()

today_expiry = expiries[0]
print(f"✓ Using expiry: {today_expiry}")

# Filter options for today's expiry
today_options = [opt for opt in options if opt['expiry'] == today_expiry]
print(f"✓ Found {len(today_options)} options for today")

# Find ATM strike (closest to current price)
all_strikes = sorted(set([opt['strike'] for opt in today_options]))
atm_strike = min(all_strikes, key=lambda x: abs(x - btc_price))

print(f"\n🎯 ATM Strike: ${atm_strike:,.0f}")
print(f"   Distance from BTC: ${abs(btc_price - atm_strike):,.2f}")

# Find ATM call and put
atm_call = None
atm_put = None

for opt in today_options:
    if opt['strike'] == atm_strike:
        if opt['type'] == 'Call':
            atm_call = opt
        elif opt['type'] == 'Put':
            atm_put = opt

# Fetch premiums
print("\n" + "="*60)
print("ATM STRIKE PREMIUMS")
print("="*60)

if atm_call:
    print(f"\n📊 ATM CALL: {atm_call['symbol']}")
    try:
        call_ticker = exchange.fetch_ticker(atm_call['symbol'])
        call_premium = call_ticker['last']
        call_bid = call_ticker.get('bid', 0)
        call_ask = call_ticker.get('ask', 0)
        
        print(f"   Strike: ${atm_strike:,.0f}")
        print(f"   Premium (Last): ${call_premium:.2f}")
        print(f"   Bid: ${call_bid:.2f}")
        print(f"   Ask: ${call_ask:.2f}")
        print(f"   Spread: ${call_ask - call_bid:.2f}")
        print(f"\n   💰 For 10 lots:")
        print(f"      Total Premium: ${call_premium * 10:,.2f}")
        print(f"      SL (150%): ${call_premium * 1.5:.2f} (Loss: ${(call_premium * 1.5 - call_premium) * 10:,.2f})")
        print(f"      TP (8%): ${call_premium * 0.08:.2f} (Profit: ${(call_premium - call_premium * 0.08) * 10:,.2f})")
    except Exception as e:
        print(f"   ❌ Error fetching premium: {e}")
else:
    print("\n❌ ATM Call not found")

if atm_put:
    print(f"\n📊 ATM PUT: {atm_put['symbol']}")
    try:
        put_ticker = exchange.fetch_ticker(atm_put['symbol'])
        put_premium = put_ticker['last']
        put_bid = put_ticker.get('bid', 0)
        put_ask = put_ticker.get('ask', 0)
        
        print(f"   Strike: ${atm_strike:,.0f}")
        print(f"   Premium (Last): ${put_premium:.2f}")
        print(f"   Bid: ${put_bid:.2f}")
        print(f"   Ask: ${put_ask:.2f}")
        print(f"   Spread: ${put_ask - put_bid:.2f}")
        print(f"\n   💰 For 10 lots:")
        print(f"      Total Premium: ${put_premium * 10:,.2f}")
        print(f"      SL (150%): ${put_premium * 1.5:.2f} (Loss: ${(put_premium * 1.5 - put_premium) * 10:,.2f})")
        print(f"      TP (8%): ${put_premium * 0.08:.2f} (Profit: ${(put_premium - put_premium * 0.08) * 10:,.2f})")
    except Exception as e:
        print(f"   ❌ Error fetching premium: {e}")
else:
    print("\n❌ ATM Put not found")

# Total straddle premium
if atm_call and atm_put:
    try:
        total_premium = call_premium + put_premium
        print(f"\n" + "="*60)
        print(f"💵 TOTAL ATM STRADDLE PREMIUM")
        print(f"="*60)
        print(f"   Call Premium: ${call_premium:.2f}")
        print(f"   Put Premium: ${put_premium:.2f}")
        print(f"   Total per lot: ${total_premium:.2f}")
        print(f"   Total for 10 lots: ${total_premium * 10:,.2f}")
        print(f"\n   Best Case (Both TP):")
        print(f"      Profit: ${(call_premium * 0.92 + put_premium * 0.92) * 10:,.2f}")
        print(f"\n   Worst Case (Both SL):")
        print(f"      Loss: ${(call_premium * 0.5 + put_premium * 0.5) * 10:,.2f}")
    except:
        pass

print("\n" + "="*60)
print("✓ Check complete!")
print("="*60)
