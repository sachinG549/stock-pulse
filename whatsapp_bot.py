"""
WhatsApp integration using Twilio API
"""
from twilio.rest import Client
import config
import logging

logger = logging.getLogger(__name__)

# Twilio rejects a WhatsApp body longer than this (error 21617).
WHATSAPP_CHAR_LIMIT = 1600
HEADLINE_CHARS = 68


def sentiment_emoji(score):
    if score > 0.3:
        return "🟢"
    if score < -0.3:
        return "🔴"
    return "🟡"


def clip(text, limit):
    """One line, truncated with an ellipsis when it does not fit."""
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    if limit <= 1:
        return text[:limit]
    return text[: limit - 1].rstrip() + "…"


def _fit_line(line, limit):
    if len(line) <= limit:
        return line
    if limit <= 1:
        return line[:limit]
    return line[: limit - 1] + "…"


def split_whatsapp_body(body, limit=WHATSAPP_CHAR_LIMIT):
    """Split a body into parts Twilio will accept.

    A report that already fits is returned as one part, with no prefix.
    Longer text is packed on line boundaries. Each part is numbered and
    stays within `limit`.
    """
    body = (body or "").strip()
    if body == "":
        return [""]
    if len(body) <= limit:
        return [body]

    def pack(max_len):
        chunks = []
        current = ""
        for raw in body.split("\n"):
            line = _fit_line(raw, max_len)
            candidate = line if current == "" else current + "\n" + line
            if len(candidate) <= max_len:
                current = candidate
                continue
            if current:
                chunks.append(current)
            current = line
        if current:
            chunks.append(current)
        return chunks

    chunks = pack(limit - len("(1/1)\n"))
    count = len(chunks)
    prefix_len = len(f"({count}/{count})\n")
    if prefix_len != len("(1/1)\n"):
        chunks = pack(limit - prefix_len)
        count = len(chunks)
    return [f"({index}/{count})\n{chunk}" for index, chunk in enumerate(chunks, 1)]


def format_stock_report(technical_results, news_insights):
    """One compact brief. A full 10-name day is meant to stay under 1600 characters."""
    lines = [f"*Stock Pulse* · {config.now_ist().strftime('%d %b %Y, %I:%M %p IST')}", ""]

    if technical_results:
        lines.append(f"*Screen* ({len(technical_results)})")
        for stock in technical_results:
            emoji = "🔥" if stock["signal"] == "BREAKOUT" else "⚡"
            lines.append(
                f"{emoji} {stock['ticker']}  ₹{stock['price']:.2f}  "
                f"{stock['price_change_pct']:+.1f}%  RSI {stock['rsi']:.0f}  "
                f"{stock['volume_ratio']:.1f}x  {stock['score']}"
            )
    else:
        lines.append("*Screen*")
        lines.append("No names passed today.")
    lines.append("")

    if news_insights.get("macro"):
        lines.append("*Macro*")
        for news in news_insights["macro"][:3]:
            lines.append(f"{sentiment_emoji(news['sentiment'])} {clip(news.get('title'), HEADLINE_CHARS)}")
        lines.append("")

    if news_insights.get("high_impact"):
        lines.append("*High impact*")
        for news in news_insights["high_impact"][:5]:
            lines.append(f"{sentiment_emoji(news['sentiment'])} {clip(news.get('title'), HEADLINE_CHARS)}")
        lines.append("")

    mentions = list((news_insights.get("stock_mentions") or {}).items())[:5]
    if mentions:
        lines.append("*In the news*")
        for ticker, items in mentions:
            title = items[0]["title"] if items else ""
            score = items[0]["sentiment"] if items else 0
            lines.append(f"{ticker} {sentiment_emoji(score)} {clip(title, HEADLINE_CHARS)}")
        lines.append("")

    lines.append("Not financial advice. DYOR.")
    return "\n".join(lines).strip() + "\n"


class WhatsAppBot:
    """Handles WhatsApp message delivery via Twilio"""

    def __init__(self):
        self.client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        self.from_number = config.TWILIO_WHATSAPP_FROM
        self.to_number = config.TARGET_PHONE_NUMBER

    def format_stock_report(self, technical_results, news_insights):
        return format_stock_report(technical_results, news_insights)

    def send_message(self, message_body):
        """
        Send one or more WhatsApp messages, each within Twilio's limit.
        Returns True only if every part is accepted.
        """
        parts = split_whatsapp_body(message_body)
        logger.info(
            "WhatsApp report is %s characters in %s part(s)",
            len(message_body or ""),
            len(parts),
        )
        for index, part in enumerate(parts, 1):
            if not self._send_one(part, index, len(parts)):
                return False
        return True

    def _send_one(self, message_body, index, total):
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=self.to_number,
            )
            logger.info(
                "Part %s/%s sent (%s characters). SID: %s status: %s",
                index,
                total,
                len(message_body),
                message.sid,
                message.status,
            )
            return True
        except Exception as e:
            logger.error("Failed to send WhatsApp part %s/%s: %s", index, total, e)
            return False

    def send_error_notification(self, error_message):
        """Send a simplified error notification if main report fails"""
        error_body = (
            f"⚠️ *STOCK PULSE - ERROR*\n"
            f"{config.now_ist().strftime('%d %b %Y, %I:%M %p IST')}\n\n"
            f"Failed to generate today's report.\n"
            f"Error: {error_message[:200]}\n\n"
            f"Please check logs for details."
        )
        return self.send_message(error_body)

    def send_test_message(self):
        """Send a test message to verify setup"""
        test_body = (
            f"✅ *TEST MESSAGE*\n"
            f"Stock Pulse bot is configured correctly!\n"
            f"Time: {config.now_ist().strftime('%d %b %Y, %I:%M %p IST')}\n\n"
            f"You will receive daily market reports at 9:00 AM IST."
        )
        return self.send_message(test_body)
