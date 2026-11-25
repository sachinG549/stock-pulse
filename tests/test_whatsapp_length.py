"""The daily brief must fit Twilio's WhatsApp character limit."""
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import config
from whatsapp_bot import WHATSAPP_CHAR_LIMIT, format_stock_report, split_whatsapp_body


def _long_title():
    return (
        "Company announces a record profit after the merger, a large contract, "
        "and an expansion that the headline keeps describing well past one line"
    )


class WhatsAppLengthTest(unittest.TestCase):
    def setUp(self):
        self._now = config.now_ist
        config.now_ist = lambda: datetime(2026, 11, 25, 9, 0, tzinfo=ZoneInfo("Asia/Kolkata"))

    def tearDown(self):
        config.now_ist = self._now

    def test_realistic_ten_name_report_is_one_message(self):
        tickers = [
            "ULTRACEMCO",
            "HINDUNILVR",
            "BHARTIARTL",
            "BAJAJ-AUTO",
            "BAJAJFINSV",
            "HEROMOTOCO",
            "ADANIPORTS",
            "ASIANPAINT",
            "POWERGRID",
            "INDUSINDBK",
        ]
        stocks = []
        for index, ticker in enumerate(tickers):
            breakout = index < 4
            stocks.append(
                {
                    "ticker": ticker,
                    "price": 99999.99 - index * 1000,
                    "price_change_pct": 12.34 if breakout else -3.21,
                    "rsi": 69.9 if breakout else 58.2,
                    "volume_ratio": 9.94,
                    "score": 100 if breakout else 55,
                    "signal": "BREAKOUT" if breakout else "MOMENTUM",
                }
            )
        title = _long_title()
        news = {
            "macro": [
                {"title": title, "sentiment": 0.8, "keywords": ["rbi", "policy"], "url": ""}
                for _ in range(3)
            ],
            "high_impact": [
                {"title": title, "sentiment": -0.7, "keywords": ["merger"], "url": ""}
                for _ in range(5)
            ],
            "stock_mentions": {
                ticker: [{"title": title, "sentiment": 0.05, "keywords": [], "url": ""}]
                for ticker in tickers[:5]
            },
        }

        body = format_stock_report(stocks, news)
        parts = split_whatsapp_body(body)

        self.assertEqual(parts, [body.strip()])
        self.assertLessEqual(len(parts[0]), WHATSAPP_CHAR_LIMIT)
        for ticker in tickers:
            self.assertIn(ticker, body)
        self.assertIn("*Macro*", body)
        self.assertIn("*High impact*", body)
        self.assertIn("*In the news*", body)
        self.assertIn("Not financial advice", body)

    def test_oversized_body_splits_inside_the_limit(self):
        body = "\n".join("x" * 120 for _ in range(40))
        parts = split_whatsapp_body(body)
        self.assertGreater(len(parts), 1)
        for part in parts:
            self.assertLessEqual(len(part), WHATSAPP_CHAR_LIMIT)
            self.assertIn("\n", part)

    def test_one_very_long_line_is_still_deliverable(self):
        parts = split_whatsapp_body("y" * 5000)
        self.assertGreaterEqual(len(parts), 1)
        for part in parts:
            self.assertLessEqual(len(part), WHATSAPP_CHAR_LIMIT)


if __name__ == "__main__":
    unittest.main()
