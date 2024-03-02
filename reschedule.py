import re
import traceback
from datetime import datetime
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from legacy_rescheduler import legacy_reschedule
from request_tracker import RequestTracker
from settings import *


def get_chrome_driver() -> WebDriver:
    options = webdriver.ChromeOptions()
    if not SHOW_GUI:
        options.add_argument("headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("disable-gpu")
    options.add_experimental_option("detach", DETACH)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    return driver


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


def get_appointment_page(driver: WebDriver) -> None:
    timeout = TIMEOUT
    continue_button = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Continue"))
    )
    continue_button.click()
    current_url = driver.current_url
    url_id = re.search(r"/(\d+)", current_url).group(1)
    appointment_url = APPOINTMENT_PAGE_URL.format(id=url_id)
    driver.get(appointment_url)


def get_available_dates(
    driver: WebDriver, request_tracker: RequestTracker
) -> list | None:
    request_tracker.log_retry()
    request_tracker.retry()
    current_url = driver.current_url
    request_url = current_url + AVAILABLE_DATE_REQUEST_SUFFIX
    request_header_cookie = "".join(
        [f"{cookie['name']}={cookie['value']};" for cookie in driver.get_cookies()]
    )
    request_headers = REQUEST_HEADERS.copy()
    request_headers["Cookie"] = request_header_cookie
    request_headers["User-Agent"] = driver.execute_script("return navigator.userAgent")
    try:
        response = requests.get(request_url, headers=request_headers)
    except Exception as e:
        print("Get available dates request failed: ", e)
        return None
    if response.status_code != 200:
        print(f"Failed with status code {response.status_code}")
        return None
    try:
        dates_json = response.json()
    except:
        print("Failed to decode json")
        return None
    dates = [datetime.strptime(item["date"], "%Y-%m-%d").date() for item in dates_json]
    return dates


def reschedule(driver: WebDriver) -> bool:
    date_request_tracker = RequestTracker(DATE_REQUEST_MAX_RETRY, DATE_REQUEST_MAX_TIME)
    while date_request_tracker.should_retry():
        dates = get_available_dates(driver, date_request_tracker)
        if not dates:
            print("Error occured when requesting available dates")
            sleep(DATE_REQUEST_DELAY)
            continue
        earliest_available_date = dates[0]
        latest_acceptable_date = datetime.strptime(
            LATEST_ACCEPTABLE_DATE, "%Y-%m-%d"
        ).date()
        if earliest_available_date <= latest_acceptable_date:
            print(
                f"{datetime.now().strftime('%H:%M:%S')} FOUND SLOT ON {earliest_available_date}!!!"
            )
            try:
                legacy_reschedule(driver)
                print("SUCCESSFULLY RESCHEDULED!!!")
                return True
            except Exception as e:
                print("Rescheduling failed: ", e)
                traceback.print_exc()
                continue
        else:
            print(
                f"{datetime.now().strftime('%H:%M:%S')} Earliest available date is {earliest_available_date}"
            )
        sleep(DATE_REQUEST_DELAY)
    return False


def reschedule_with_new_session() -> bool:
    driver = get_chrome_driver()
    session_failures = 0
    while session_failures < NEW_SESSION_AFTER_FAILURES:
        try:
            login(driver)
            get_appointment_page(driver)
            break
        except Exception as e:
            print("Unable to get appointment page: ", e)
            session_failures += 1
            sleep(FAIL_RETRY_DELAY)
            continue
    rescheduled = reschedule(driver)
    if rescheduled:
        return True
    else:
        driver.quit()
        return False


if __name__ == "__main__":
    session_count = 0
    while True:
        session_count += 1
        print(f"Attempting with new session #{session_count}")
        rescheduled = reschedule_with_new_session()
        sleep(NEW_SESSION_DELAY)
        if rescheduled:
            break
