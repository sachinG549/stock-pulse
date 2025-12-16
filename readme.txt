# 🚀 Pre-Market Stock Pulse

**Never Miss a Market Move Again** - Automated daily WhatsApp alerts for high-momentum Indian stocks with news catalysts.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## 🎯 What Does This Do?

Every morning at **9:00 AM IST**, you'll receive a comprehensive WhatsApp report containing:

- 📈 **Top 10 Technical Breakouts** - Stocks showing strong momentum (Price > 50-EMA, RSI 50-70, High Volume)
- 🌍 **Macro Events** - Fed decisions, inflation data, geopolitical events affecting markets
- 💥 **High-Impact News** - Corporate actions (mergers, demergers, results) with sentiment analysis
- 📰 **Stock-Specific Mentions** - News about your breakout stocks with sentiment scores

**Example WhatsApp Message:**
```
🚀 PRE-MARKET STOCK PULSE
📅 16 Dec 2025, 09:00 AM IST
===================================

📈 TOP TECHNICAL BREAKOUTS

🔥 RELIANCE
   Price: ₹2,845.30 (🟢 +2.34%)
   RSI: 64.2 | Vol: 2.1x
   Signal: BREAKOUT (Score: 85/100)

⚡ TCS
   Price: ₹3,621.75 (🟢 +1.87%)
   RSI: 58.4 | Vol: 1.8x
   Signal: MOMENTUM (Score: 72/100)

🌍 MACRO EVENTS

🟢 US Fed holds rates steady, signals 2025 cuts...
   Keywords: fed, interest rate, policy

💥 HIGH-IMPACT NEWS

🟢 Reliance announces strategic partnership with...
   Tags: acquisition, expansion, growth

===================================
⚠️ DISCLAIMER: Not financial advice. DYOR.
🤖 Powered by Stock Pulse AI
```

---

## ✨ Key Features

### 🧠 Smart Analysis Engine
- **Technical Screening**: EMA crossovers, RSI, volume spikes
- **Sentiment Analysis**: NLP-powered news scoring using VADER
- **High-Impact Detection**: Automatically flags mergers, results, policy changes
- **Customizable Parameters**: Adjust thresholds to match your risk appetite

### 🔒 Production-Ready Architecture
- **Error-Proof**: Comprehensive try-catch blocks, fallback mechanisms
- **Modular Design**: Separate modules for analysis, news, and messaging
- **Secure**: All API keys via environment variables, no hardcoded secrets
- **Logging**: Detailed logs for debugging and monitoring

### ☁️ Flexible Deployment
- **GitHub Actions** (Free, recommended)
- **AWS Lambda** (Scalable)
- **Render.com** (Simple)
- **Local Cron** (Full control)

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
git clone <your-repo-url>
cd stock-pulse
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp .env.example .env
# Edit .env with your API keys
```

**Get Your Free API Keys:**
- **NewsAPI**: https://newsapi.org/register (100 requests/day free)
- **Twilio**: https://www.twilio.com/try-twilio (Free trial with $15 credit)

### 3. Setup WhatsApp
1. Go to Twilio Console → Messaging → WhatsApp Sandbox
2. Send the join code from your WhatsApp to the Twilio number
3. Update `TARGET_PHONE_NUMBER` in `.env`

### 4. Test Everything
```bash
python main.py --test
```

You should receive a test WhatsApp message! ✅

### 5. Deploy (GitHub Actions)
```bash
# Add secrets to GitHub repo
gh secret set NEWSAPI_KEY
gh secret set TWILIO_ACCOUNT_SID
gh secret set TWILIO_AUTH_TOKEN
gh secret set TARGET_PHONE_NUMBER

# Push to GitHub - it will run daily at 9 AM IST automatically!
git push origin main
```

---

## 📁 Project Structure

```
stock-pulse/
├── main.py                 # Orchestrator (entry point)
├── analyzer.py             # Technical & sentiment analysis
├── whatsapp_bot.py         # Twilio WhatsApp integration
├── config.py               # Configuration & API keys
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── DEPLOYMENT_GUIDE.md     # Detailed deployment instructions
└── README.md               # This file
```

---

## 🔧 Configuration

### Adjust Technical Parameters (`config.py`)

```python
# Technical Analysis
EMA_PERIOD = 50              # Exponential Moving Average period
RSI_LOWER_BOUND = 50         # Minimum RSI for breakout
RSI_UPPER_BOUND = 70         # Maximum RSI (avoid overbought)
VOLUME_MULTIPLIER = 1.5      # Volume should be 1.5x of 20-day avg
MIN_PRICE = 50               # Ignore penny stocks below ₹50
MAX_STOCKS_TO_REPORT = 10    # Top N stocks in report

# News Analysis
NEWS_LOOKBACK_DAYS = 1       # Fetch news from last N days
HIGH_IMPACT_KEYWORDS = [
    'demerger', 'acquisition', 'merger', 'record profit',
    # ... add your keywords
]
```

### Custom Stock Universe

Replace the default tickers with your own:

```python
# Option 1: Manual list
DEFAULT_TICKERS = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']

# Option 2: Load from CSV
import pandas as pd
df = pd.read_csv('nifty500.csv')
DEFAULT_TICKERS = df['Symbol'].tolist()
```

---

## 📊 How It Works

### 1. Technical Analysis Pipeline
```python
For each stock:
  ├── Fetch 3-month historical data (yfinance)
  ├── Calculate EMA(50), RSI(14), Volume ratio
  ├── Check breakout conditions:
  │   ├── Price > EMA(50) ✓
  │   ├── 50 < RSI < 70 ✓
  │   └── Volume > 1.5x average ✓
  ├── Assign score (0-100)
  └── Return top 10 stocks
```

### 2. News Analysis Pipeline
```python
Fetch news → Extract headlines → NLP sentiment → Check keywords
                                        ↓
                    High-Impact? → Flag and categorize
                    Macro Event? → Separate section
                    Stock mention? → Link to ticker
```

### 3. Delivery System
```python
Format report → Twilio API → WhatsApp → Your phone ✅
```

---

## 🧪 Testing

### Run All Tests
```bash
python main.py --test
```

This validates:
- ✅ Environment variables
- ✅ Technical analysis module
- ✅ NewsAPI connectivity
- ✅ WhatsApp delivery

### Manual Report Generation
```bash
python main.py --run
```

### Check Logs
```bash
tail -f stock_pulse.log
```

---

## 🌐 Deployment Options

| Platform | Cost | Difficulty | Best For |
|----------|------|------------|----------|
| **GitHub Actions** | Free | ⭐⭐ | Most users |
| **AWS Lambda** | ~Free | ⭐⭐⭐ | Advanced users |
| **Render.com** | Free | ⭐ | Beginners |
| **Local Cron** | Free | ⭐⭐⭐⭐ | Full control |

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## 🔍 Troubleshooting

### "No stocks found"
- **Cause**: Market consolidation or strict parameters
- **Fix**: Lower `RSI_LOWER_BOUND` or `VOLUME_MULTIPLIER` in config

### "WhatsApp not received"
- **Cause**: Not joined Twilio sandbox
- **Fix**: Send join code to Twilio WhatsApp number

### "NewsAPI rate limit"
- **Cause**: Exceeded 100 requests/day (free tier)
- **Fix**: Reduce `NEWS_LOOKBACK_DAYS` or upgrade plan

### "GitHub Action not running"
- **Cause**: Incorrect cron syntax or disabled workflow
- **Fix**: Check UTC timezone conversion, enable workflow

---

## 🛡️ Disclaimer

This software is for **educational purposes only**. It provides automated analysis but **is not financial advice**.

- ⚠️ Past performance does not guarantee future results
- ⚠️ Always conduct your own research (DYOR)
- ⚠️ Consult a licensed financial advisor before trading
- ⚠️ The developers are not responsible for any trading losses

---

## 🤝 Contributing

Contributions are welcome! Ideas for improvements:

- [ ] Add more technical indicators (MACD, Bollinger Bands)
- [ ] Implement backtesting module
- [ ] Store historical signals in database
- [ ] Add Telegram/Email delivery options
- [ ] Create web dashboard with Streamlit
- [ ] Machine learning for signal accuracy prediction

---

## 📜 License

MIT License - Feel free to use, modify, and distribute.

---

## 🙏 Acknowledgments

Built with:
- [yfinance](https://github.com/ranaroussi/yfinance) - Market data
- [NewsAPI](https://newsapi.org/) - News aggregation
- [VADER Sentiment](https://github.com/cjhutto/vaderSentiment) - NLP analysis
- [Twilio](https://www.twilio.com/) - WhatsApp delivery

---

## 📧 Support

Having issues? Found a bug?

1. Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Review logs in `stock_pulse.log`
3. Open an issue on GitHub with logs

---

**Made with ❤️ for traders who value their time**

*"The stock market is filled with individuals who know the price of everything, but the value of nothing." - Philip Fisher*