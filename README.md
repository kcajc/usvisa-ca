# US Visa Rescheduler for Canada

A simple Python script for making US visa interview appointments in Canada

## Update

- The core functionality is still working (as of **March 2026**) according to users' report
- Gmail-related code might error out, but it doesn't block rescheduling
- Adopt this repo: this project is looking for a new maintainer, open an issue if you'd like to adopt it.

## Features

- Automatically checks for available visa interview slots at your selected consulate
- Supports multiple consulate locations across Canada
- Configurable date ranges for appointment scheduling
- Email notifications when appointments are found or rescheduled
- Support for excluding specific date ranges
- Headless operation mode for unattended running
- Test mode for safe testing without actual rescheduling
- Automatic retry mechanism with configurable delays
- Support for multiple applicants in a single appointment

## Prerequisites

- Python 3.x installed
- An existing US visa appointment booked on <https://ais.usvisa-info.com/en-ca/>
- Gmail account for notifications (optional but recommended)

## Installation

1. Clone this repository
2. Install dependencies:

```
pip install -r requirements.txt
```

Supported Consulate locations:

```
CONSULATES = {
    "Calgary": 89,
    "Halifax": 90,
    "Montreal": 91,
    "Ottawa": 92,
    "Quebec": 93,
    "Toronto": 94,
    "Vancouver": 95
} # Only Toronto and Vancouver consulates are verified
```

Add a new `.env` file to the root of the project, this file will be used to configure parameters for the script.

### Required fields

These **must** be set, or the script will fail on startup / cannot log in:

| Variable | Description |
|---|---|
| `USER_EMAIL` | The email address for your <https://ais.usvisa-info.com/en-ca/niv/users/sign_in> account |
| `USER_PASSWORD` | The password for your <https://ais.usvisa-info.com/en-ca/niv/users/sign_in> account |
| `EARLIEST_ACCEPTABLE_DATE` | The earliest interview date you are looking for (`YYYY-MM-DD`) |
| `LATEST_ACCEPTABLE_DATE` | The latest acceptable interview date (`YYYY-MM-DD`) |
| `USER_CONSULATE` | Use one of the consulate names listed above. Only Toronto and Vancouver are verified |

### Optional fields

These can be left blank; the script will still run and simply skip the related feature.

| Variable | Description |
|---|---|
| `GMAIL_SENDER_NAME` | Name of sender on email notifications |
| `GMAIL_EMAIL` | Sender Gmail account |
| `GMAIL_APPLICATION_PWD` | App password for the sender account — see [Google's app password guide](https://support.google.com/mail/answer/185833?hl=en) |
| `RECEIVER_NAME` | Recipient name for notifications |
| `RECEIVER_EMAIL` | Recipient email for notifications |
| `EXCLUSION_START_DATE_{i}` / `EXCLUSION_END_DATE_{i}` | Start/end of an excluded date range, where `i` is `1`–`9` (up to 9 ranges). Each pair must be provided together |
| `DEBUG` / `LOG_LEVEL` | Set `DEBUG=1` (or `LOG_LEVEL=DEBUG`) to enable verbose debug logging — see [Debug logging](#debug-logging) below |

> **Note on Gmail fields:** `GMAIL_SENDER_NAME`, `GMAIL_EMAIL`, `GMAIL_APPLICATION_PWD`, `RECEIVER_NAME`, and `RECEIVER_EMAIL` are all-or-nothing — if any of the five is missing, email notifications are skipped entirely (with a warning logged) and rescheduling still proceeds normally.

Example `.env`:

```
USER_EMAIL=""   # required
USER_PASSWORD=""    # required
EARLIEST_ACCEPTABLE_DATE="" # required
LATEST_ACCEPTABLE_DATE=""   # required
USER_CONSULATE="" # required
GMAIL_SENDER_NAME=""    # optional
GMAIL_EMAIL=""  # optional
GMAIL_APPLICATION_PWD=""    # optional
RECEIVER_NAME=""    # optional
RECEIVER_EMAIL=""   # optional
EXCLUSION_START_DATE_1=""   # optional
EXCLUSION_END_DATE_1=""     # optional
EXCLUSION_START_DATE_2=""   # optional
EXCLUSION_END_DATE_2=""     # optional
DEBUG="1"   # optional, enables debug logging
```

You can add up to 9 exclusion date ranges. Each date range to be excluded using the syntax `EXCLUSION_START_DATE_{i}` and `EXCLUSION_END_DATE_{i}` where `i` can be replaced by numbers between 1 to 9.

### Find a slot and book it automatically

```
python reschedule.py
```

See the script in action. Once you're satisfied with its functionality, set `TEST_MODE` to `False` in `settings.py`. For a headless operation, you can also set `SHOW_GUI` to `False` and allow the script to run unattended.

Note `detect_and_notify.py` is no longer maintained.

## Caution

It may not always be feasible to reschedule an appointment multiple times. Therefore, it's crucial to use `TEST_MODE = True` for testing purposes and ensure the `LATEST_ACCEPTABLE_DATE` is genuinely acceptable to you.

Consulates other than Toronto and Vancouver are not tested.

## Contribution

Please feel free to report issues. PRs are welcomed and greatly appreciated!

One improvement I'm interested in is rewriting `legacy_rescheduler` using `requests`.

## Special thanks

Huge thanks to [@jywyq](https://github.com/jywyq) for adding the Gmail notification feature.

Huge thanks to [@bsingh-kpt](https://github.com/bsingh-kpt) for (finally!) fixing the `legacy_rescheduler` in Mar 2025.

Thanks to [@trungnguyen21](https://github.com/trungnguyen21) and [@saroopskesav](https://github.com/saroopskesav) for helping with the consulate numbers in other cities.

## Disclaimer

This script is provided as-is for the purpose of assisting individuals in rescheduling appointments. While it has been developed with care and with the intention of being helpful, it comes with no guarantees or warranties of any kind, either expressed or implied. By using this script, you acknowledge and agree that you are doing so at your own risk. The author(s) or contributor(s) of this script shall not be held liable for any direct or indirect damages that arise from its use. Please ensure that you understand the actions performed by this script before running it, and consider the ethical and legal implications of its use in your context.
