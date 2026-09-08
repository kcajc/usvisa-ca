import re
import os
import smtplib
import ssl
import traceback
from datetime import datetime
from email.message import EmailMessage
from time import sleep
from typing import Union, List

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from legacy_rescheduler import legacy_reschedule
from request_tracker import RequestTracker
from settings import *


def log_message(message: str) -> None:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def get_chrome_driver() -> WebDriver:
    options = webdriver.ChromeOptions()
    chrome_binary = os.getenv("CHROME_BIN")
    if chrome_binary:
        options.binary_location = chrome_binary
    if not SHOW_GUI:
        options.add_argument("headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("disable-gpu")
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36')
    options.add_experimental_option("detach", DETACH)
    options.add_argument('--incognito')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--user-data-dir=/tmp/chrome-{datetime.now().strftime("%Y%m%d-%H%M%S")}')
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH")
    service = Service(executable_path=chromedriver_path) if chromedriver_path else Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def validate_settings() -> None:
    missing = [
        name for name, value in (
            ("USER_EMAIL", USER_EMAIL),
            ("USER_PASSWORD", USER_PASSWORD),
            ("EARLIEST_ACCEPTABLE_DATE", EARLIEST_ACCEPTABLE_DATE),
            ("LATEST_ACCEPTABLE_DATE", LATEST_ACCEPTABLE_DATE),
            ("USER_CONSULATE", USER_CONSULATE),
        ) if not value
    ]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    if CONSULATE_ID is None:
        raise ValueError(
            f"Unsupported USER_CONSULATE '{USER_CONSULATE}'. "
            f"Choose one of: {', '.join(CONSULATES)}"
        )
    earliest = datetime.strptime(EARLIEST_ACCEPTABLE_DATE, "%Y-%m-%d").date()
    latest = datetime.strptime(LATEST_ACCEPTABLE_DATE, "%Y-%m-%d").date()
    if earliest > latest:
        raise ValueError("EARLIEST_ACCEPTABLE_DATE must not be after LATEST_ACCEPTABLE_DATE")
    if SMTP_SECURITY not in {"starttls", "ssl", "none"}:
        raise ValueError("SMTP_SECURITY must be one of: starttls, ssl, none")
    if not 1 <= SMTP_PORT <= 65535:
        raise ValueError("SMTP_PORT must be between 1 and 65535")
    if bool(TELEGRAM_BOT_TOKEN) != bool(TELEGRAM_CHAT_ID):
        raise ValueError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be configured together"
        )


def smtp_is_configured() -> bool:
    return all((SMTP_HOST, SMTP_FROM, SMTP_TO))


def telegram_is_configured() -> bool:
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)


def send_smtp_notification(subject: str, text: str) -> bool:
    if not smtp_is_configured():
        return False
    try:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = SMTP_FROM
        message["To"] = SMTP_TO
        message.set_content(text)

        if SMTP_SECURITY == "ssl":
            smtp = smtplib.SMTP_SSL(
                SMTP_HOST,
                SMTP_PORT,
                timeout=20,
                context=ssl.create_default_context(),
            )
        else:
            smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20)
        with smtp:
            smtp.ehlo()
            if SMTP_SECURITY == "starttls":
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
            if SMTP_USERNAME:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(message)
        log_message("SMTP notification sent")
        return True
    except Exception as error:
        log_message(f"SMTP notification failed: {error}")
        return False


def send_telegram_notification(subject: str, text: str) -> bool:
    if not telegram_is_configured():
        return False
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": f"{subject}\n\n{text}"},
            timeout=20,
        )
        response.raise_for_status()
        log_message("Telegram notification sent")
        return True
    except Exception as error:
        # Request exceptions can include the URL, which contains the bot token.
        log_message(f"Telegram notification failed: {type(error).__name__}")
        return False


def send_notification(subject: str, text: str) -> None:
    configured = smtp_is_configured() or telegram_is_configured()
    send_smtp_notification(subject, text)
    send_telegram_notification(subject, text)
    if not configured:
        log_message("Notification skipped because no SMTP or Telegram channel is configured")


def date_is_excluded(appointment_date) -> bool:
    return any(
        datetime.strptime(start, "%Y-%m-%d").date()
        <= appointment_date
        <= datetime.strptime(end, "%Y-%m-%d").date()
        for start, end in EXCLUSION_DATE_RANGES
    )


def acceptable_dates(dates):
    earliest = datetime.strptime(EARLIEST_ACCEPTABLE_DATE, "%Y-%m-%d").date()
    latest = datetime.strptime(LATEST_ACCEPTABLE_DATE, "%Y-%m-%d").date()
    return sorted(
        appointment_date
        for appointment_date in dates
        if earliest <= appointment_date <= latest
        and not date_is_excluded(appointment_date)
    )


def completion_exists() -> bool:
    return bool(COMPLETION_FILE and os.path.exists(COMPLETION_FILE))


def mark_completed() -> None:
    if not COMPLETION_FILE:
        return
    parent = os.path.dirname(COMPLETION_FILE)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(COMPLETION_FILE, "w", encoding="utf-8") as marker:
        marker.write(datetime.now().isoformat() + "\n")


def idle_after_completion() -> None:
    if not IDLE_AFTER_SUCCESS:
        return
    log_message("Appointment task is complete; container is idling")
    while True:
        sleep(3600)


def capture_diagnostics(driver: WebDriver, label: str) -> None:
    if not DIAGNOSTICS_DIR:
        return
    try:
        os.makedirs(DIAGNOSTICS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = os.path.join(DIAGNOSTICS_DIR, f"{label}-{timestamp}.png")
        driver.save_screenshot(path)
        log_message(f"Saved browser screenshot to {path}")
        log_message(f"Browser page title: {driver.title}")
    except Exception as error:
        log_message(f"Unable to save browser diagnostics: {error}")


def login(driver: WebDriver) -> None:
    driver.get(LOGIN_URL)
    timeout = TIMEOUT

    email_input = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.ID, "user_email"))
    )
    email_input.send_keys(USER_EMAIL)

    password_input = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.ID, "user_password"))
    )
    password_input.send_keys(USER_PASSWORD)

    policy_checkbox = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "icheckbox"))
    )
    policy_checkbox.click()

    login_button = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.NAME, "commit"))
    )
    login_button.click()


def _find_visible_action(driver: WebDriver, label: str):
    locators = (
        (By.LINK_TEXT, label),
        (By.XPATH, f"//button[normalize-space()='{label}']"),
        (By.XPATH, f"//input[@value='{label}']"),
    )
    for locator in locators:
        for element in driver.find_elements(*locator):
            if element.is_displayed() and element.is_enabled():
                return element
    return False


def _click_action_if_present(
    driver: WebDriver, label: str, timeout: float
) -> bool:
    try:
        action = WebDriverWait(driver, timeout).until(
            lambda current_driver: _find_visible_action(current_driver, label)
        )
    except TimeoutException:
        return False
    action.click()
    sleep(2)
    return True


def _has_visible_element(driver: WebDriver, locator) -> bool:
    return any(
        element.is_displayed()
        for element in driver.find_elements(*locator)
    )


def _appointment_page_state(driver: WebDriver):
    if _has_visible_element(
        driver, (By.ID, "appointments_consulate_appointment_date_input")
    ):
        return "ready"
    if _has_visible_element(
        driver, (By.ID, "appointments_consulate_appointment_facility_id")
    ):
        return "facility"
    if _find_visible_action(driver, "Schedule Appointment"):
        return "schedule"
    if _has_visible_element(driver, (By.CLASS_NAME, "icheckbox")):
        return "policy"
    return False


def _prepare_appointment_page(driver: WebDriver) -> None:
    timeout = TIMEOUT
    for _ in range(3):
        state = WebDriverWait(driver, timeout).until(_appointment_page_state)
        if state == "ready":
            return
        if state == "facility":
            facility = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(
                    (By.ID, "appointments_consulate_appointment_facility_id")
                )
            )
            Select(facility).select_by_value(str(CONSULATE_ID))
            log_message(f"Selected {USER_CONSULATE} consulate")
            sleep(2)
            continue
        if state == "schedule":
            _click_action_if_present(driver, "Schedule Appointment", timeout)
            continue

        policy_checkbox = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "icheckbox"))
        )
        policy_checkbox.click()
        continue_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.NAME, "commit"))
        )
        continue_button.click()

    WebDriverWait(driver, timeout).until(
        lambda current_driver: _appointment_page_state(current_driver) == "ready"
    )


def get_appointment_page(driver: WebDriver) -> None:
    timeout = TIMEOUT

    # Newer flows show a group-action page with this link. Older flows first
    # show a Continue link and then expose Schedule Appointment.
    if not _click_action_if_present(driver, "Schedule Appointment", 2):
        if not _click_action_if_present(driver, "Continue", timeout):
            raise TimeoutException(
                "Could not find either 'Schedule Appointment' or 'Continue'"
            )
        _click_action_if_present(driver, "Schedule Appointment", timeout)

    current_url = driver.current_url
    schedule_match = re.search(r"/schedule/(\d+)", current_url)
    if not schedule_match:
        raise RuntimeError(f"Could not find schedule id in URL: {current_url}")

    appointment_url = APPOINTMENT_PAGE_URL.format(id=schedule_match.group(1))
    driver.get(appointment_url)


def get_available_dates(
    driver: WebDriver, request_tracker: RequestTracker
) -> Union[List[datetime.date], None]:
    request_tracker.log_retry()
    request_tracker.retry()
    schedule_base = driver.current_url.split("/appointment")[0]
    request_url = schedule_base + "/appointment" + AVAILABLE_DATE_REQUEST_SUFFIX
    request_header_cookie = "".join(
        [f"{cookie['name']}={cookie['value']};" for cookie in driver.get_cookies()]
    )
    request_headers = REQUEST_HEADERS.copy()
    request_headers["Cookie"] = request_header_cookie
    request_headers["User-Agent"] = driver.execute_script("return navigator.userAgent")
    try:
        response = requests.get(request_url, headers=request_headers)
    except Exception as e:
        log_message(f"Get available dates request failed: {e}")
        return None
    if response.status_code != 200:
        log_message(f"Failed with status code {response.status_code}")
        log_message(f"Response Text: {response.text}")
        return None
    try:
        dates_json = response.json()
    except:
        log_message("Failed to decode json")
        log_message(f"Response Text: {response.text}")
        return None
    dates = [datetime.strptime(item["date"], "%Y-%m-%d").date() for item in dates_json]
    return dates


def reschedule(driver: WebDriver, retryCount: int = 0) -> bool:
    date_request_tracker = RequestTracker(
        retryCount if (retryCount > 0) else DATE_REQUEST_MAX_RETRY,
        DATE_REQUEST_DELAY * retryCount if (retryCount > 0) else DATE_REQUEST_MAX_TIME
    )
    while date_request_tracker.should_retry():
        dates = get_available_dates(driver, date_request_tracker)
        if not dates:
            log_message("Error occured when requesting available dates")
            sleep(DATE_REQUEST_DELAY)
            continue
        matching_dates = acceptable_dates(dates)
        if matching_dates:
            earliest_available_date = matching_dates[0]
            log_message(f"FOUND SLOT ON {earliest_available_date}!!!")
            try:
                if legacy_reschedule(driver, earliest_available_date):
                    send_notification(
                        f"Visa Appointment Rescheduled for {earliest_available_date}",
                        f"Your visa appointment has been successfully rescheduled to {earliest_available_date} at {USER_CONSULATE} consulate.",
                    )
                    log_message("SUCCESSFULLY RESCHEDULED!!!")
                    return True
                return False
            except Exception as e:
                log_message(f"Rescheduling failed: {e}")
                traceback.print_exc()
                continue
        else:
            log_message(f"Earliest available date is {min(dates)}")
        sleep(DATE_REQUEST_DELAY)
    return False


def reschedule_with_new_session(retryCount: int = DATE_REQUEST_MAX_RETRY) -> bool:
    for session_attempt in range(1, NEW_SESSION_AFTER_FAILURES + 1):
        driver = None
        try:
            driver = get_chrome_driver()
            login(driver)
            get_appointment_page(driver)
            _prepare_appointment_page(driver)
            try:
                return reschedule(driver, retryCount)
            finally:
                driver.quit()
        except Exception as e:
            current_url = driver.current_url if driver else "browser startup"
            log_message(
                f"Unable to get appointment page at {current_url}: "
                f"{type(e).__name__}: {e}"
            )
            if driver:
                capture_diagnostics(driver, f"session-{session_attempt}")
                driver.quit()
            if session_attempt < NEW_SESSION_AFTER_FAILURES:
                sleep(FAIL_RETRY_DELAY)
    return False


if __name__ == "__main__":
    validate_settings()
    if completion_exists():
        log_message(f"Completion marker found at {COMPLETION_FILE}; no booking will be attempted")
        idle_after_completion()
        raise SystemExit(0)

    session_count = 0
    log_message(f"Attempting to reschedule for email: {USER_EMAIL}")
    log_message(f"User Consulate: {USER_CONSULATE}")
    log_message(f"Earliest Acceptable Date: {EARLIEST_ACCEPTABLE_DATE}")
    log_message(f"Latest Acceptable Date: {LATEST_ACCEPTABLE_DATE}")
    if NOTIFY_ON_STARTUP:
        send_notification(
            "US Visa Rescheduler Started",
            f"Monitoring {USER_CONSULATE} for dates from "
            f"{EARLIEST_ACCEPTABLE_DATE} to {LATEST_ACCEPTABLE_DATE}.",
        )

    if EXCLUSION_DATE_RANGES:
        log_message("Excluded Date Ranges:")
        for i, (start, end) in enumerate(EXCLUSION_DATE_RANGES, 1):
            log_message(f"  Range {i}: {start} to {end}")
    else:
        log_message("No date ranges excluded")

    while True:
        session_count += 1
        log_message(f"Attempting with new session #{session_count}")
        rescheduled = reschedule_with_new_session()
        if rescheduled:
            break
        sleep(NEW_SESSION_DELAY)
    mark_completed()
    idle_after_completion()
