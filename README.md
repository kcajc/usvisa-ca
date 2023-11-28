# US Visa Re-scheduler for Canada

**⚠️ This project is no longer maintained. Please make a PR if you have a fix or want to improve its poor engineering practices.**

An Extremely Simple Python Script for Making US Visa Interview Appointment in Canada

## Setup

Make sure you have booked an appointment on https://ais.usvisa-info.com/en-ca/.

Install dependencies (requires Python3):
```sh
pip install selenium webdriver_manager
```

Modify the following code in the script with instructions in the script:

```python3
USER_EMAIL = "name@gmail.com"
USER_PASSWORD = "yourpassword"
MAX_WAIT_MONTH = 6
```

Run the script:

```sh
python findslot.py
```

## Optimization

Use `FOUND_SLOT_RETRY_DELAY` and `NO_SLOT_RETRY_DELAY` (in seconds) to change the the wait between attempts.

```python3
FOUND_SLOT_RETRY_DELAY = 180
NO_SLOT_RETRY_DELAY = 180
```

Please note that a shorter delay may result in not finding any avalible slot. 180 seconds is tested to be safe for now.

2023-11-27: verified the script working fine. reschedule Succesfully.
