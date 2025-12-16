"""
Configuration file for Pre-Market Stock Pulse
All sensitive data is loaded from environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Print for debugging (remove in production)
print(f"Config loaded. NewsAPI Key present: {bool('8046be0a1df8479bbbbbebc6ae773ddb')}")

# API Configuration
NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.environ.get('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
TARGET_PHONE_NUMBER = os.environ.get('TARGET_PHONE_NUMBER')  # Format: whatsapp:+919876543210

# Market Configuration
NIFTY_500_TICKERS_FILE = 'nifty500_tickers.csv'  # Optional: Load from CSV
# Fallback: Top 50 liquid stocks for demo
DEFAULT_TICKERS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
    'ICICIBANK.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS',
    'AXISBANK.NS', 'LT.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'HCLTECH.NS',
    'WIPRO.NS', 'BAJFINANCE.NS', 'TITAN.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS',
    'SUNPHARMA.NS', 'TECHM.NS', 'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS',
    'M&M.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'ADANIPORTS.NS', 'COALINDIA.NS',
    'BAJAJFINSV.NS', 'HDFCLIFE.NS', 'SBILIFE.NS', 'DIVISLAB.NS', 'DRREDDY.NS',
    'APOLLOHOSP.NS', 'CIPLA.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS', 'GRASIM.NS',
    'HINDALCO.NS', 'JSWSTEEL.NS', 'BRITANNIA.NS', 'INDUSINDBK.NS', 'SHREECEM.NS',
    'BAJAJ-AUTO.NS', 'ADANIENT.NS', 'TATACONSUM.NS', 'VEDL.NS', 'BPCL.NS'
]

# Technical Analysis Parameters
EMA_PERIOD = 50
RSI_LOWER_BOUND = 50
RSI_UPPER_BOUND = 70
VOLUME_MULTIPLIER = 1.5  # Current volume should be 1.5x of 20-day average
MIN_PRICE = 50  # Minimum stock price to consider (to avoid penny stocks)
MAX_STOCKS_TO_REPORT = 10  # Top N stocks to include in report

# News Analysis Parameters
NEWS_LOOKBACK_DAYS = 1  # Fetch news from last N days
HIGH_IMPACT_KEYWORDS = [
    'demerger', 'acquisition', 'merger', 'record profit', 'breakthrough',
    'sanction', 'ban', 'approval', 'launch', 'expansion', 'contract',
    'dividend', 'buyback', 'ipo', 'listing', 'quarterly results',
    'earnings beat', 'revenue growth', 'profit surge', 'loss', 'downgrade'
]

MACRO_KEYWORDS = [
    'fed', 'interest rate', 'inflation', 'gdp', 'war', 'conflict',
    'policy', 'budget', 'election', 'oil price', 'crude', 'rbi',
    'monetary policy', 'recession', 'rally', 'crash'
]

# Validation
def validate_config():
    """Validate that all required environment variables are set"""
    missing = []
    
    if not NEWSAPI_KEY:
        missing.append('NEWSAPI_KEY')
    if not TWILIO_ACCOUNT_SID:
        missing.append('TWILIO_ACCOUNT_SID')
    if not TWILIO_AUTH_TOKEN:
        missing.append('TWILIO_AUTH_TOKEN')
    if not TARGET_PHONE_NUMBER:
        missing.append('TARGET_PHONE_NUMBER')
    
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please set them in your .env file or environment."
        )
    
    return True