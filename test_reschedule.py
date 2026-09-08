import unittest
from datetime import date
from unittest.mock import patch

import reschedule


class RescheduleHelpersTest(unittest.TestCase):
    def test_acceptable_dates_scans_past_excluded_earliest_date(self):
        dates = [date(2026, 10, 2), date(2026, 10, 9), date(2027, 1, 1)]
        with (
            patch.object(reschedule, "EARLIEST_ACCEPTABLE_DATE", "2026-10-01"),
            patch.object(reschedule, "LATEST_ACCEPTABLE_DATE", "2026-12-31"),
            patch.object(
                reschedule,
                "EXCLUSION_DATE_RANGES",
                [("2026-10-01", "2026-10-07")],
            ),
        ):
            self.assertEqual(reschedule.acceptable_dates(dates), [date(2026, 10, 9)])

    def test_smtp_starttls_notification(self):
        with (
            patch.object(reschedule, "SMTP_HOST", "smtp.example.com"),
            patch.object(reschedule, "SMTP_PORT", 587),
            patch.object(reschedule, "SMTP_SECURITY", "starttls"),
            patch.object(reschedule, "SMTP_USERNAME", "sender@example.com"),
            patch.object(reschedule, "SMTP_PASSWORD", "app-password"),
            patch.object(reschedule, "SMTP_FROM", "sender@example.com"),
            patch.object(reschedule, "SMTP_TO", "receiver@example.com"),
            patch("reschedule.smtplib.SMTP") as smtp_class,
        ):
            self.assertTrue(reschedule.send_smtp_notification("Subject", "Body"))

        smtp = smtp_class.return_value
        smtp.starttls.assert_called_once()
        smtp.login.assert_called_once_with("sender@example.com", "app-password")
        smtp.send_message.assert_called_once()

    def test_telegram_notification(self):
        with (
            patch.object(reschedule, "TELEGRAM_BOT_TOKEN", "bot-token"),
            patch.object(reschedule, "TELEGRAM_CHAT_ID", "chat-id"),
            patch("reschedule.requests.post") as post,
        ):
            self.assertTrue(reschedule.send_telegram_notification("Subject", "Body"))

        post.assert_called_once_with(
            "https://api.telegram.org/botbot-token/sendMessage",
            data={"chat_id": "chat-id", "text": "Subject\n\nBody"},
            timeout=20,
        )
        post.return_value.raise_for_status.assert_called_once()


if __name__ == "__main__":
    unittest.main()
