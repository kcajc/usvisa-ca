# Account Info
USER_EMAIL = ""
USER_PASSWORD = ""

# Say you want an appointment no later than Mar 14, 2024
# Please strictly follow the YYYY-MM-DD format
EARLIEST_ACCEPTABLE_DATE = "2024-07-23"
LATEST_ACCEPTABLE_DATE = "2025-01-29"

# The following is only required for the Gmail notification feature
# Gmail login info
GMAIL_SENDER_NAME = ""
GMAIL_EMAIL = ""
GMAIL_APPLICATION_PWD = ""

# Email notification receiver info
RECEIVER_NAME = ""
RECEIVER_EMAIL = ""

# Override with local, for developers
# from local import *

# See the automation in action
SHOW_GUI = True  # toggle to false if you don't want to see the browser

# If you just want to see the program run WITHOUT clicking the confirm reschedule button
# For testing, also set a date really far away so the app actually tries to reschedule
TEST_MODE = True

# Don't change the following unless you know what you are doing
DETACH = True
NEW_SESSION_AFTER_FAILURES = 5
NEW_SESSION_DELAY = 60
TIMEOUT = 10
FAIL_RETRY_DELAY = 30
DATE_REQUEST_DELAY = 30
DATE_REQUEST_MAX_RETRY = 60
DATE_REQUEST_MAX_TIME = 30 * 60
LOGIN_URL = "https://ais.usvisa-info.com/en-ca/niv/users/sign_in"
AVAILABLE_DATE_REQUEST_SUFFIX = "/days/94.json?appointments[expedite]=false"
APPOINTMENT_PAGE_URL = "https://ais.usvisa-info.com/en-ca/niv/schedule/{id}/appointment"
PAYMENT_PAGE_URL = "https://ais.usvisa-info.com/en-ca/niv/schedule/{id}/payment"
REQUEST_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
}
