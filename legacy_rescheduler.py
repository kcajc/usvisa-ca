from time import sleep
from datetime import datetime, date

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver

from settings import TEST_MODE, NUM_PARTICIPANTS

# This is frankly very, very bad and should be rewritten with requests
# when I get a test account
def legacy_reschedule(driver: WebDriver, date_to_book: date):
    driver.refresh()

    # Continue btn: applicable when there are more than one applicant for scheduling
    if NUM_PARTICIPANTS > 1:
        continueBtn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//main[@id='main']/div[@class='mainContent']/form/div[2]/div/input"))
            )
        continueBtn.click()

    date_selection_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.ID, 'appointments_consulate_appointment_date_input'
            )
        )
    )
    sleep(2)
    date_selection_box.click()

    # Move to next month
    def next_month():
        driver.find_element(By.XPATH, "//div[@id='ui-datepicker-div']/div[2]/div/a").click()

    # Check if avalible in current month
    def cur_month_ava():
        month = driver.find_element(By.XPATH, "//div[@id='ui-datepicker-div']/div[1]/table/tbody")
        dates = month.find_elements(By.TAG_NAME, "td")
        for date in dates:
            if date.get_attribute("class") == " undefined":
                ava_date_btn = date.find_element(By.TAG_NAME, "a")
                return True
        return False

    # Check the nearest slot is avalible in # months (0 for this month, 1 for next month...) and move to the month
    def nearest_ava():
        ava_in = 0
        cur = cur_month_ava()
        while not cur:
            next_month()
            cur = cur_month_ava()
            ava_in += 1
        return ava_in

    avalible_in_months = nearest_ava()

    # Reschedule if the avalible_in_months is less than or equal to wait month
    print("Trying to pick time and reschedule...")
    month = driver.find_element(By.XPATH, "//div[@id='ui-datepicker-div']/div[1]/table/tbody")
    dates = month.find_elements(By.TAG_NAME, "td")
    ava_date_btn = None
    for date in dates:
        if date.get_attribute("class") == " undefined":
            ava_date_btn = date.find_element(By.TAG_NAME, "a")
            break
    ava_date_btn.click()

    # confirm selected date
    sleep(2)
    date_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.ID, 'appointments_consulate_appointment_date'
            )
        )
    )
    date_selected = datetime.strptime(date_box.get_attribute('value'), "%Y-%m-%d").date()
    print(date_selected)
    if not date_selected <= date_to_book:
        print(f"{datetime.now().strftime('%H:%M:%S')} SLOT '{date_to_book}' no longer available\n")
        return False
    else:
        print(f"{datetime.now().strftime('%H:%M:%S')} SLOT '{date_selected}' is still available. Booking....\n")

    # Select time of the date:
    sleep(2)
    appointment_time = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "appointments_consulate_appointment_time"))
    )
    appointment_time.click()
    appointment_time_options = appointment_time.find_elements(By.TAG_NAME, "option")
    appointment_time_options[len(appointment_time_options) - 1].click()

    # Click "Reschedule"
    driver.find_element(
        By.XPATH,
        "//form[@id='appointment-form']/div[2]/fieldset/ol/li/input",
    ).click()
    sleep(2)
    try:
        confirm = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div/div/a[2]"))
        )
    finally:
        sleep(2)
        driver.implicitly_wait(0.1)
        if not TEST_MODE:
            confirm.click()
            return True

    return False
