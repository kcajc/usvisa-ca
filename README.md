# US Visa Rescheduler for Canada

~~This project is no longer maintained. Please make a PR if you have a fix or want to improve its poor engineering practices.~~
Surprisingly, this project has proven to be more useful than initially thought. I will try to maintain it as long as possible, given my availability and access to test accounts.

A simple Python script for making US visa interview appointments in Canada

## Setup

Make sure you have booked an appointment on https://ais.usvisa-info.com/en-ca/.

Install dependencies (Python3 is required):
```sh
pip install selenium webdriver_manager requests
```

Modify `settings.py` as per the instructions within the script:

```python3
USER_EMAIL = "name@gmail.com"
USER_PASSWORD = "yourpassword"
LATEST_ACCEPTABLE_DATE = "2024-03-14"
```

Run the script:

```sh
python reschedule.py
```

See the script in action. Once you're satisfied with its functionality, set `TEST_MODE` to `False` in `settings.py`. For a headless operation, you can also set `SHOW_GUI` to `False` and allow the script to run unattended.

## Caution

It may not always be feasible to reschedule an appointment multiple times. Therefore, it's crucial to use `TEST_MODE = True` for testing purposes and ensure the `LATEST_ACCEPTABLE_DATE` is genuinely acceptable to you.

## Contribution

Please feel free to report issues. PRs are welcomed and greatly appreciated!

The script can be flaky especially for the `legacy_rescheduler`.  Plans are in place to rewrite it using `requests`, but a test account is needed.

## Disclaimer

This script is provided as-is for the purpose of assisting individuals in rescheduling appointments. While it has been developed with care and with the intention of being helpful, it comes with no guarantees or warranties of any kind, either expressed or implied. By using this script, you acknowledge and agree that you are doing so at your own risk. The author(s) or contributor(s) of this script shall not be held liable for any direct or indirect damages that arise from its use. Please ensure that you understand the actions performed by this script before running it, and consider the ethical and legal implications of its use in your context.
