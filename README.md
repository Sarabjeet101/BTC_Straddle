# Delta Exchange India Trading Bot

This project automates crypto trading on Delta Exchange India using the CCXT library.

## Setup

1. Install required packages:
   ```
   pip install ccxt python-dotenv
   ```

2. Create a `.env` file with your API credentials:
   ```
   DELTA_API_KEY=your_api_key_here
   DELTA_API_SECRET=your_api_secret_here
   ```

3. Run the connection test:
   ```
   python test_connection.py
   ```

## Project Structure

- `config.py` - Configuration and API credentials loader
- `test_connection.py` - Test exchange connection
- `trading_bot.py` - Main trading bot logic
- `.env` - API credentials (not tracked in git)

## Important Notes

- Keep your API keys secure and never commit them to version control
- Test with small amounts first
- Delta Exchange India uses the 'delta' exchange ID in CCXT
