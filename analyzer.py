"""
Core analysis engine for technical screening and sentiment analysis
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Handles technical analysis and stock screening"""
    
    def __init__(self, tickers):
        self.tickers = tickers
        
    def calculate_ema(self, prices, period):
        """Calculate Exponential Moving Average"""
        return prices.ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def fetch_stock_data(self, ticker, period='3mo'):
        """Fetch historical data for a single ticker"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                logger.warning(f"No data found for {ticker}")
                return None
            
            return hist
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    def analyze_stock(self, ticker):
        """
        Perform complete technical analysis on a single stock
        Returns dict with analysis results or None if criteria not met
        """
        try:
            hist = self.fetch_stock_data(ticker)
            if hist is None or len(hist) < config.EMA_PERIOD + 20:
                return None
            
            # Calculate indicators
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2]
            
            # Skip penny stocks
            if current_price < config.MIN_PRICE:
                return None
            
            # EMA calculation
            ema_50 = self.calculate_ema(hist['Close'], config.EMA_PERIOD).iloc[-1]
            
            # RSI calculation
            rsi = self.calculate_rsi(hist['Close']).iloc[-1]
            
            # Volume analysis
            avg_volume_20d = hist['Volume'].iloc[-20:].mean()
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume_20d if avg_volume_20d > 0 else 0
            
            # Price change
            price_change_pct = ((current_price - previous_close) / previous_close) * 100
            
            # Breakout criteria
            is_above_ema = current_price > ema_50
            is_rsi_in_range = config.RSI_LOWER_BOUND < rsi < config.RSI_UPPER_BOUND
            is_high_volume = volume_ratio > config.VOLUME_MULTIPLIER
            
            # Score calculation (0-100)
            score = 0
            if is_above_ema:
                score += 30
            if is_rsi_in_range:
                score += 25
            if is_high_volume:
                score += 25
            if price_change_pct > 2:
                score += 20
            
            # Only return stocks that meet minimum criteria
            if is_above_ema and (is_rsi_in_range or is_high_volume):
                return {
                    'ticker': ticker.replace('.NS', ''),
                    'price': round(current_price, 2),
                    'price_change_pct': round(price_change_pct, 2),
                    'rsi': round(rsi, 2),
                    'volume_ratio': round(volume_ratio, 2),
                    'ema_50': round(ema_50, 2),
                    'score': score,
                    'signal': 'BREAKOUT' if score >= 70 else 'MOMENTUM'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {str(e)}")
            return None
    
    def screen_stocks(self):
        """Screen all stocks and return top candidates"""
        logger.info(f"Screening {len(self.tickers)} stocks...")
        results = []
        
        for ticker in self.tickers:
            analysis = self.analyze_stock(ticker)
            if analysis:
                results.append(analysis)
        
        # Sort by score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Found {len(results)} stocks matching criteria")
        return results[:config.MAX_STOCKS_TO_REPORT]


class NewsAnalyzer:
    """Handles news fetching and sentiment analysis"""
    
    def __init__(self, api_key):
        self.newsapi = NewsApiClient(api_key=api_key)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
    def fetch_market_news(self):
        """Fetch general market and macro news"""
        try:
            from_date = (datetime.now() - timedelta(days=config.NEWS_LOOKBACK_DAYS)).strftime('%Y-%m-%d')
            
            # Fetch India-specific business news
            india_news = self.newsapi.get_everything(
                q='India stock market OR Nifty OR Sensex OR NSE OR BSE',
                language='en',
                from_param=from_date,
                sort_by='relevancy',
                page_size=20
            )
            
            # Fetch global macro news
            macro_news = self.newsapi.get_everything(
                q='Federal Reserve OR inflation OR GDP OR oil price OR war OR recession',
                language='en',
                from_param=from_date,
                sort_by='relevancy',
                page_size=20
            )
            
            all_articles = []
            if india_news.get('articles'):
                all_articles.extend(india_news['articles'])
            if macro_news.get('articles'):
                all_articles.extend(macro_news['articles'])
            
            logger.info(f"Fetched {len(all_articles)} news articles")
            return all_articles
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []
    
    def fetch_stock_specific_news(self, stock_names):
        """Fetch news for specific stocks"""
        try:
            from_date = (datetime.now() - timedelta(days=config.NEWS_LOOKBACK_DAYS)).strftime('%Y-%m-%d')
            
            # Create query for top stocks
            query = ' OR '.join(stock_names[:5])  # Limit to top 5 to avoid query length issues
            
            stock_news = self.newsapi.get_everything(
                q=query,
                language='en',
                from_param=from_date,
                sort_by='relevancy',
                page_size=30
            )
            
            return stock_news.get('articles', [])
            
        except Exception as e:
            logger.error(f"Error fetching stock-specific news: {str(e)}")
            return []
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text using VADER"""
        if not text:
            return 0
        
        scores = self.sentiment_analyzer.polarity_scores(text)
        return scores['compound']  # Returns value between -1 (negative) and +1 (positive)
    
    def check_high_impact_keywords(self, text):
        """Check if text contains high-impact keywords"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_keywords = [kw for kw in config.HIGH_IMPACT_KEYWORDS if kw in text_lower]
        return found_keywords
    
    def check_macro_keywords(self, text):
        """Check if text contains macro event keywords"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_keywords = [kw for kw in config.MACRO_KEYWORDS if kw in text_lower]
        return found_keywords
    
    def process_news(self, articles, stock_list=None):
        """
        Process news articles and return categorized insights
        stock_list: list of stock tickers to match against
        """
        high_impact_news = []
        macro_news = []
        stock_mentions = {}
        
        for article in articles:
            title = article.get('title', '')
            description = article.get('description', '')
            full_text = f"{title} {description}"
            
            sentiment = self.analyze_sentiment(full_text)
            high_impact_kw = self.check_high_impact_keywords(full_text)
            macro_kw = self.check_macro_keywords(full_text)
            
            # Check for stock mentions
            if stock_list:
                for stock in stock_list:
                    stock_name = stock.replace('.NS', '').upper()
                    if stock_name in full_text.upper():
                        if stock_name not in stock_mentions:
                            stock_mentions[stock_name] = []
                        stock_mentions[stock_name].append({
                            'title': title,
                            'sentiment': sentiment,
                            'keywords': high_impact_kw,
                            'url': article.get('url', '')
                        })
            
            # Categorize news
            if high_impact_kw and abs(sentiment) > 0.3:
                high_impact_news.append({
                    'title': title,
                    'sentiment': sentiment,
                    'keywords': high_impact_kw,
                    'url': article.get('url', '')
                })
            
            if macro_kw and abs(sentiment) > 0.2:
                macro_news.append({
                    'title': title,
                    'sentiment': sentiment,
                    'keywords': macro_kw,
                    'url': article.get('url', '')
                })
        
        return {
            'high_impact': high_impact_news[:5],  # Top 5
            'macro': macro_news[:3],  # Top 3
            'stock_mentions': stock_mentions
        }