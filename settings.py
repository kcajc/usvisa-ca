from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Account Info
USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")
NUM_PARTICIPANTS = 1

# Say you want an appointment no later than Mar 14, 2024
# Please strictly follow the YYYY-MM-DD format for all dates

EARLIEST_ACCEPTABLE_DATE = os.getenv("EARLIEST_ACCEPTABLE_DATE")
LATEST_ACCEPTABLE_DATE = os.getenv("LATEST_ACCEPTABLE_DATE")

# Date exclusion ranges
EXCLUSION_DATE_RANGES = []
for i in range(1, 10):  # Support up to 9 exclusion ranges
    start = os.getenv(f"EXCLUSION_START_DATE_{i}")
    end = os.getenv(f"EXCLUSION_END_DATE_{i}")
    if start and end:
        EXCLUSION_DATE_RANGES.append((start, end))

# Your consulate's city
CONSULATES = {
    "Calgary": 89,
    "Halifax": 90,
    "Montreal": 91,
    "Ottawa": 92,
    "Quebec": 93,
    "Toronto": 94,
    "Vancouver": 95
} # Only Toronto and Vancouver consulates are verified
# Choose a city from the list above
USER_CONSULATE = os.getenv("USER_CONSULATE")

# The following is only required for the Gmail notification feature
# Gmail login info
GMAIL_SENDER_NAME = os.getenv("GMAIL_SENDER_NAME")
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_APPLICATION_PWD = os.getenv("GMAIL_APPLICATION_PWD")

# Email notification receiver info
RECEIVER_NAME = os.getenv("RECEIVER_NAME")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# Override with local, for developers
# from local import *

# See the automation in action
SHOW_GUI = False  # toggle to false if you don't want to see the browser

# If you just want to see the program run WITHOUT clicking the confirm reschedule button
# For testing, also set a date really far away so the app actually tries to reschedule
TEST_MODE = False

# Don't change the following unless you know what you are doing
DETACH = True
NEW_SESSION_AFTER_FAILURES = 5
NEW_SESSION_DELAY = 300
TIMEOUT = 10
FAIL_RETRY_DELAY = 180
DATE_REQUEST_DELAY = 180
DATE_REQUEST_MAX_RETRY = 5
DATE_REQUEST_MAX_TIME = 15 * 60
LOGIN_URL = "https://ais.usvisa-info.com/en-ca/niv/users/sign_in"
AVAILABLE_DATE_REQUEST_SUFFIX = f"/days/{CONSULATES[USER_CONSULATE]}.json?appointments[expedite]=false"
APPOINTMENT_PAGE_URL = "https://ais.usvisa-info.com/en-ca/niv/schedule/{id}/appointment"
PAYMENT_PAGE_URL = "https://ais.usvisa-info.com/en-ca/niv/schedule/{id}/payment"
REQUEST_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
}
