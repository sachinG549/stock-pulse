"""
Main orchestrator for Pre-Market Stock Pulse
Run this script daily at 9:00 AM IST via scheduler
"""
import sys
import logging
from datetime import datetime
import config
from analyzer import TechnicalAnalyzer, NewsAnalyzer
from whatsapp_bot import WhatsAppBot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_pulse.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_analysis():
    """
    Main function to orchestrate the entire workflow
    Returns: (technical_results, news_insights) tuple or (None, None) on failure
    """
    try:
        logger.info("=" * 60)
        logger.info("STARTING PRE-MARKET STOCK PULSE ANALYSIS")
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
        logger.info("=" * 60)
        
        # Step 1: Technical Analysis
        logger.info("\n📊 Step 1: Running Technical Analysis...")
        technical_analyzer = TechnicalAnalyzer(config.DEFAULT_TICKERS)
        technical_results = technical_analyzer.screen_stocks()
        
        if technical_results:
            logger.info(f"✅ Found {len(technical_results)} stocks with breakout signals")
            for stock in technical_results[:3]:
                logger.info(f"   - {stock['ticker']}: {stock['signal']} (Score: {stock['score']})")
        else:
            logger.warning("⚠️ No stocks met the technical criteria today")
        
        # Step 2: News Analysis
        logger.info("\n📰 Step 2: Fetching and Analyzing News...")
        news_analyzer = NewsAnalyzer(config.NEWSAPI_KEY)
        
        # Fetch general market news
        market_news = news_analyzer.fetch_market_news()
        logger.info(f"   Fetched {len(market_news)} general market articles")
        
        # Fetch stock-specific news if we have results
        stock_news = []
        if technical_results:
            stock_names = [s['ticker'] for s in technical_results]
            stock_news = news_analyzer.fetch_stock_specific_news(stock_names)
            logger.info(f"   Fetched {len(stock_news)} stock-specific articles")
        
        # Combine and process all news
        all_news = market_news + stock_news
        stock_list = [s['ticker'] + '.NS' for s in technical_results] if technical_results else []
        news_insights = news_analyzer.process_news(all_news, stock_list)
        
        logger.info(f"✅ News Analysis Complete:")
        logger.info(f"   - High-Impact News: {len(news_insights['high_impact'])}")
        logger.info(f"   - Macro Events: {len(news_insights['macro'])}")
        logger.info(f"   - Stock Mentions: {len(news_insights['stock_mentions'])}")
        
        return technical_results, news_insights
        
    except Exception as e:
        logger.error(f"❌ Error in analysis pipeline: {str(e)}", exc_info=True)
        return None, None


def send_daily_report():
    """
    Main entry point: Run analysis and send WhatsApp report
    """
    try:
        # Validate configuration
        logger.info("🔍 Validating configuration...")
        config.validate_config()
        logger.info("✅ Configuration validated")
        
        # Run analysis
        technical_results, news_insights = run_analysis()
        
        # Check if we have any data to report
        if technical_results is None and news_insights is None:
            raise Exception("Analysis pipeline failed completely")
        
        # Initialize WhatsApp bot
        logger.info("\n📱 Step 3: Preparing WhatsApp Report...")
        bot = WhatsAppBot()
        
        # Format and send message
        message = bot.format_stock_report(
            technical_results or [],
            news_insights or {'high_impact': [], 'macro': [], 'stock_mentions': {}}
        )
        
        logger.info("\n📤 Sending report via WhatsApp...")
        success = bot.send_message(message)
        
        if success:
            logger.info("✅ Report sent successfully!")
            logger.info("=" * 60)
            logger.info("DAILY REPORT COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            return True
        else:
            raise Exception("Failed to send WhatsApp message")
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ CRITICAL ERROR: {error_msg}", exc_info=True)
        
        # Try to send error notification
        try:
            bot = WhatsAppBot()
            bot.send_error_notification(error_msg)
        except:
            logger.error("Failed to send error notification")
        
        logger.info("=" * 60)
        logger.info("DAILY REPORT FAILED")
        logger.info("=" * 60)
        return False


def test_setup():
    """
    Test function to verify all components are working
    Run this before deploying to production
    """
    print("\n🧪 TESTING STOCK PULSE SETUP")
    print("=" * 60)
    
    # Test 1: Configuration
    print("\n1️⃣ Testing Configuration...")
    try:
        config.validate_config()
        print("   ✅ All environment variables are set")
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    # Test 2: Technical Analysis
    print("\n2️⃣ Testing Technical Analysis...")
    try:
        analyzer = TechnicalAnalyzer(config.DEFAULT_TICKERS[:5])
        results = analyzer.screen_stocks()
        print(f"   ✅ Technical analysis works (tested {5} stocks)")
        if results:
            print(f"   Found {len(results)} potential stocks")
    except Exception as e:
        print(f"   ❌ Technical analysis error: {e}")
        return False
    
    # Test 3: News API
    print("\n3️⃣ Testing News API...")
    try:
        news_analyzer = NewsAnalyzer(config.NEWSAPI_KEY)
        articles = news_analyzer.fetch_market_news()
        print(f"   ✅ News API works (fetched {len(articles)} articles)")
    except Exception as e:
        print(f"   ❌ News API error: {e}")
        return False
    
    # Test 4: WhatsApp Integration
    print("\n4️⃣ Testing WhatsApp Integration...")
    try:
        bot = WhatsAppBot()
        success = bot.send_test_message()
        if success:
            print("   ✅ WhatsApp test message sent!")
        else:
            print("   ❌ Failed to send WhatsApp message")
            return False
    except Exception as e:
        print(f"   ❌ WhatsApp error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! Setup is complete.")
    print("=" * 60)
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Pre-Market Stock Pulse')
    parser.add_argument('--test', action='store_true', help='Run setup tests')
    parser.add_argument('--run', action='store_true', help='Run daily report')
    
    args = parser.parse_args()
    
    if args.test:
        test_setup()
    elif args.run:
        send_daily_report()
    else:
        # Default: run daily report
        send_daily_report()