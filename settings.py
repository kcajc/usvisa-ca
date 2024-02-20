# Account Info
USER_EMAIL = "name@gmail.com"
USER_PASSWORD = "yourpassword"

# Say you want an appointment no later than Mar 14, 2024
# Please strictly follow the YYYY-MM-DD format
LATEST_ACCEPTABLE_DATE = "2024-03-14"

# See the automation in action
SHOW_GUI = True

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
APPOINTMENT_PAGE_URL = "https://ais.usvisa-info.com/en-ca/niv/schedule/{id}/appointment"
AVAILABLE_DATE_REQUEST_SUFFIX = "/days/94.json?appointments[expedite]=false"
REQUEST_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
}
