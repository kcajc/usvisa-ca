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
- An existing US visa appointment booked on https://ais.usvisa-info.com/en-ca/
- Gmail account for notifications (optional but recommended)

## Installation

1. Clone this repository
2. Install dependencies:

```sh
pip install -r requirements.txt
```

Supported Consulate locations:

```python
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

## Docker / NAS deployment

Prebuilt multi-architecture images for `linux/amd64` and `linux/arm64` are
published to GitHub Container Registry:

```sh
docker pull ghcr.io/kcajc/usvisa-ca:latest
```

For a NAS deployment, download `compose.yml` and `.env.example`, then:

```sh
cp .env.example .env
# Edit .env and keep TEST_MODE=true for the first run.
mkdir -p data/diagnostics data/state
docker compose up -d
docker compose logs -f usvisa-ca
```

No inbound port is required. The `./data` directory stores a completion marker
after a successful reschedule, so a NAS or container restart will not start a
second booking attempt. To intentionally start a new search, stop the container,
delete `data/state/reschedule-complete`, update `.env`, and start it again.
Failed browser sessions save screenshots under `data/diagnostics` to make
headless login and site-layout problems easier to diagnose. Review screenshots
for personal information before sharing them.

### Notifications

Notifications are sent after a successful reschedule. SMTP and Telegram are
independent: configure either one or both. A notification failure does not turn
a successful booking into a failure or trigger another booking attempt.

Generic SMTP with STARTTLS (commonly port 587):

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_SECURITY=starttls
SMTP_USERNAME=notification@example.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=Visa Bot <notification@example.com>
SMTP_TO=recipient@example.com
```

For implicit TLS, commonly on port 465, use `SMTP_SECURITY=ssl`. For a trusted
local mail relay that does not use authentication, leave `SMTP_USERNAME` and
`SMTP_PASSWORD` empty. `SMTP_SECURITY=none` disables transport encryption and
should only be used on a trusted local network.

Telegram Bot:

```env
TELEGRAM_BOT_TOKEN=123456789:replace-with-your-bot-token
TELEGRAM_CHAT_ID=replace-with-your-chat-id
```

Set `NOTIFY_ON_STARTUP=true` temporarily to send a startup message through every
configured channel. Change it back to `false` after verifying delivery, or a
message will be sent every time the container restarts.

The previous Gmail variables remain supported and are translated to
`smtp.gmail.com:587` with STARTTLS. Gmail requires an application password; do
not use or share the normal account password.

Images are built by GitHub Actions on pushes to `main`. A tag such as `v1.2.3`
also publishes `1.2.3` and `1.2` image tags. The package must be public in the
repository's GitHub Packages settings for anonymous `docker pull` access.

Add a new `.env` file to the root of the project, this file will be used to configure parameters for the script. You can use the following parameters:

```
USER_EMAIL=""   # The email address for your https://ais.usvisa-info.com/en-ca/niv/users/sign_in account
USER_PASSWORD=""    # The password for your  https://ais.usvisa-info.com/en-ca/niv/users/sign_in account
EARLIEST_ACCEPTABLE_DATE="" # The earliest interview date you are looking for
LATEST_ACCEPTABLE_DATE=""   # The latest acceptable interview date
USER_CONSULATE="" # Use one of the cosulate names from above
GMAIL_SENDER_NAME=""    # Name of sender on email
GMAIL_EMAIL=""  # Sender email account
GMAIL_APPLICATION_PWD=""    # Use the app password you generated for application -- check https://support.google.com/mail/answer/185833?hl=en
RECEIVER_NAME=""    # Recipient name
RECEIVER_EMAIL=""   # Recipient email
EXCLUSION_START_DATE_1=""   # Start date for first excluded date range
EXCLUSION_END_DATE_1=""     # End date for first excluded date range
EXCLUSION_START_DATE_2=""   # Start date for second excluded date range
EXCLUSION_END_DATE_2=""     # End date for second excluded date range
```

You can add upto 9 exclusion date ranges. Each date range to be excluded using the syntax `EXCLUSION_START_DATE_{i}` and `EXCLUSION_END_DATE_{i}` where `i` can be replaced by numbers between 1 to 9.

### Find a slot and book it automatically

```sh
python reschedule.py
```

See the script in action. `TEST_MODE` defaults to `True`; once you're satisfied
with its functionality, set `TEST_MODE=false` in `.env`. For headless operation,
leave `SHOW_GUI=false` and allow the script to run unattended.

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
