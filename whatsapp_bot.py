"""
WhatsApp integration using Twilio API
"""
from twilio.rest import Client
from datetime import datetime
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppBot:
    """Handles WhatsApp message delivery via Twilio"""
    
    def __init__(self):
        self.client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        self.from_number = config.TWILIO_WHATSAPP_FROM
        self.to_number = config.TARGET_PHONE_NUMBER
        
    def format_stock_report(self, technical_results, news_insights):
        """
        Format the complete report as a clean WhatsApp message
        """
        lines = []
        
        # Header
        lines.append("🚀 *PRE-MARKET STOCK PULSE*")
        lines.append(f"📅 {datetime.now().strftime('%d %b %Y, %I:%M %p IST')}")
        lines.append("=" * 35)
        lines.append("")
        
        # Technical Breakouts Section
        if technical_results:
            lines.append("📈 *TOP TECHNICAL BREAKOUTS*")
            lines.append("")
            
            for i, stock in enumerate(technical_results, 1):
                emoji = "🔥" if stock['signal'] == 'BREAKOUT' else "⚡"
                change_emoji = "🟢" if stock['price_change_pct'] > 0 else "🔴"
                
                lines.append(f"{emoji} *{stock['ticker']}*")
                lines.append(f"   Price: ₹{stock['price']} ({change_emoji} {stock['price_change_pct']:+.2f}%)")
                lines.append(f"   RSI: {stock['rsi']} | Vol: {stock['volume_ratio']:.1f}x")
                lines.append(f"   Signal: {stock['signal']} (Score: {stock['score']}/100)")
                lines.append("")
        else:
            lines.append("📈 *TECHNICAL ANALYSIS*")
            lines.append("No strong breakouts detected today.")
            lines.append("")
        
        # Macro News Section
        if news_insights['macro']:
            lines.append("🌍 *MACRO EVENTS*")
            lines.append("")
            
            for news in news_insights['macro']:
                sentiment_emoji = "🟢" if news['sentiment'] > 0.3 else "🔴" if news['sentiment'] < -0.3 else "🟡"
                lines.append(f"{sentiment_emoji} {news['title'][:100]}...")
                if news['keywords']:
                    lines.append(f"   Keywords: {', '.join(news['keywords'][:3])}")
                lines.append("")
        
        # High Impact News Section
        if news_insights['high_impact']:
            lines.append("💥 *HIGH-IMPACT NEWS*")
            lines.append("")
            
            for news in news_insights['high_impact']:
                sentiment_emoji = "🟢" if news['sentiment'] > 0.3 else "🔴" if news['sentiment'] < -0.3 else "🟡"
                lines.append(f"{sentiment_emoji} {news['title'][:100]}...")
                if news['keywords']:
                    lines.append(f"   Tags: {', '.join(news['keywords'][:3])}")
                lines.append("")
        
        # Stock-Specific News Mentions
        if news_insights['stock_mentions']:
            lines.append("📰 *STOCK IN NEWS*")
            lines.append("")
            
            for stock, mentions in list(news_insights['stock_mentions'].items())[:5]:
                lines.append(f"• *{stock}*: {len(mentions)} mention(s)")
                if mentions:
                    sentiment = mentions[0]['sentiment']
                    sentiment_emoji = "🟢" if sentiment > 0.3 else "🔴" if sentiment < -0.3 else "🟡"
                    lines.append(f"  {sentiment_emoji} {mentions[0]['title'][:80]}...")
                lines.append("")
        
        # Footer
        lines.append("=" * 35)
        lines.append("⚠️ *DISCLAIMER*: This is automated analysis.")
        lines.append("Not financial advice. DYOR before trading.")
        lines.append("")
        lines.append("🤖 Powered by Stock Pulse AI")
        
        return "\n".join(lines)
    
    def send_message(self, message_body):
        """
        Send WhatsApp message via Twilio
        Returns True if successful, False otherwise
        """
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=self.to_number
            )
            
            logger.info(f"Message sent successfully. SID: {message.sid}")
            logger.info(f"Message status: {message.status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            return False
    
    def send_error_notification(self, error_message):
        """Send a simplified error notification if main report fails"""
        try:
            error_body = (
                f"⚠️ *STOCK PULSE - ERROR*\n"
                f"{datetime.now().strftime('%d %b %Y, %I:%M %p IST')}\n\n"
                f"Failed to generate today's report.\n"
                f"Error: {error_message[:200]}\n\n"
                f"Please check logs for details."
            )
            
            message = self.client.messages.create(
                body=error_body,
                from_=self.from_number,
                to=self.to_number
            )
            
            logger.info(f"Error notification sent. SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send error notification: {str(e)}")
            return False
    
    def send_test_message(self):
        """Send a test message to verify setup"""
        test_body = (
            f"✅ *TEST MESSAGE*\n"
            f"Stock Pulse bot is configured correctly!\n"
            f"Time: {datetime.now().strftime('%d %b %Y, %I:%M %p IST')}\n\n"
            f"You will receive daily market reports at 9:00 AM IST."
        )
        
        return self.send_message(test_body)