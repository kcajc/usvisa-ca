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

from request_tracker import RequestTracker
from reschedule import get_chrome_driver, login
from settings import *

from gmail import GMail, Message


def notify_receiver(title_str: str, msg_str: str):
    gmail = GMail(f"{GMAIL_SENDER_NAME} <{GMAIL_EMAIL}>", GMAIL_APPLICATION_PWD)  # Sender gmail
    msg = Message(title_str ,to=f'{RECEIVER_NAME} <{RECEIVER_EMAIL}>',text=msg_str)
    gmail.send(msg)
    print(f"Email sent to {RECEIVER_EMAIL}:", title_str, msg_str)

def get_dates_from_payment_page(driver: WebDriver) -> None:
    timeout = TIMEOUT
    continue_button = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Continue"))
    )
    continue_button.click()
    current_url = driver.current_url
    url_id = re.search(r"/(\d+)", current_url).group(1)
    payment_url = PAYMENT_PAGE_URL.format(id=url_id)
    driver.get(payment_url)

    content_table = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "for-layout"))
    )
    text_elements = content_table.find_elements(By.TAG_NAME, "td")
    loc_str_array = [e.text for i,e in enumerate(text_elements) if i%2==0]
    date_str_array = [e.text for i,e in enumerate(text_elements) if i%2==1]
    return loc_str_array, date_str_array


def detect_and_notify(loc_str_array: list, date_str_array: list) -> bool:
    earliest_acceptable_date = datetime.strptime(
        EARLIEST_ACCEPTABLE_DATE, "%Y-%m-%d"
    ).date()
    latest_acceptable_date = datetime.strptime(
        LATEST_ACCEPTABLE_DATE, "%Y-%m-%d"
    ).date()

    length = len(loc_str_array)
    detected = False
    for i in range(length):
        loc_str = loc_str_array[i]
        date_str = date_str_array[i]
        if date_str == "No Appointments Available":
            continue
        date = datetime.strptime(
            date_str, "%d %B, %Y"
        ).date()
        
        if earliest_acceptable_date <= date <= latest_acceptable_date:
            print(
                f"{datetime.now().strftime('%H:%M:%S')} FOUND SLOT ON {date}, location: {loc_str}!!!, sending email..."
            )
            notify_receiver(f"New slot found with date: {date}, location: {loc_str}", f"New slot found with date: {date}, location: {loc_str}")
            detected = True
        else:
            print(
                f"{datetime.now().strftime('%H:%M:%S')} Earliest available date is {date}, location: {loc_str}"
            )
    return detected


def detect_with_new_session() -> bool:
    driver = get_chrome_driver()
    session_failures = 0
    detected = False
    while session_failures < NEW_SESSION_AFTER_FAILURES:
        try:
            login(driver)
            loc_str_array, date_str_array = get_dates_from_payment_page(driver)
            detected = detect_and_notify(loc_str_array, date_str_array)
            break
        except Exception as e:
            print("Unable to get payment page: ", e)
            session_failures += 1
            sleep(FAIL_RETRY_DELAY)
            continue
    driver.quit()
    return detected


if __name__ == "__main__":
    session_count = 0

    while True:
        session_count += 1
        print(f"Attempting with new session #{session_count}")
        detected = detect_with_new_session()
        sleep(NEW_SESSION_DELAY)
        if detected:
            sleep(600)
            print("Yay!!!")
