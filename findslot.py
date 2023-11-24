from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait as Wait
from webdriver_manager.chrome import ChromeDriverManager
import os

########################################
# Modify the following lines
########################################

# Your email and password for ais.usvisa-info.com
USER_EMAIL = "name@gmail.com"
USER_PASSWORD = "yourpassword"

# Use "True" if you want to see Chrome in action, leave as "False" otherwise
SHOW_GUI = True

# The number of months you would wait 
# Enter 0 if you only want slots in this month;
# Enter 1 if you want slots in this month or next month (as early as possible);
# Enter 2 if you want slots in this month or the next months (as early as possible);
# And so on
MAX_WAIT_MONTH = 6

# You are advised to use the default values for the following variables
# The number of seconds before retry, when there's a slot (but wait time is too long)/when there's no slot
# The default values are tested, a wait time that's too short may result in failed requests
FOUND_SLOT_RETRY_DELAY = 180
NO_SLOT_RETRY_DELAY = 180
########################################
# Do not modify the lines below
########################################

SIGNIN_PAGE = "https://ais.usvisa-info.com/en-ca/niv/users/sign_in"

def attempt(email, pw, wait, slots):
    # Set chrome options
    options = webdriver.ChromeOptions()
    if not SHOW_GUI:
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")

    # Initialize webdriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Visit sign-in page
    driver.get(SIGNIN_PAGE)

    # Find/type email/password and checkbox
    email_input = driver.find_element(By.NAME, "user[email]")
    email_input.send_keys(email)
    password_input = driver.find_element(By.NAME, "user[password]")
    password_input.send_keys(pw)
    checkbox = driver.find_element(By.CLASS_NAME, "icheckbox")
    checkbox.click()
    btn = driver.find_element(By.NAME, "commit")
    btn.click()
    
    Wait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Continue')]")))
    print("\tlogin successful!")

    # Land in appointment page, click "Continue"
    continue_link = driver.find_element(By.LINK_TEXT, 'Continue')
    continue_link.click()

    # Jump to appointment dates page
    cur_url = driver.current_url
    appointment_url = cur_url.replace("continue_actions", "appointment")
    driver.get(appointment_url)

    # Get appointment date selection box
    driver.implicitly_wait(0.3)
    try:
        date_selection_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/main/div[4]/div/div/form/fieldset/ol/fieldset/div/div[2]/div[3]/label[1]"))
        )
        date_selection_box.click()
    # If the date selection box is not clickerable, there's no slot avalible
    except:
        return -2

    # Move to next month
    def next_month():
        driver.find_element(By.XPATH, "/html/body/div[5]/div[2]/div/a").click()


    # Check if avalible in current month 
    def cur_month_ava():
        month = driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/table/tbody')
        dates = month.find_elements(By.TAG_NAME, 'td')
        for date in dates:
            if date.get_attribute('class') == ' undefined':
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
    slots[avalible_in_months] = slots[avalible_in_months] + 1 if avalible_in_months in slots else 1

    # Reschedule if the avalible_in_months is less than or equal to wait month
    if avalible_in_months <= wait:
        print("Avalible slot in {} months found, trying to pick time and reschedule...".format(avalible_in_months))
        month = driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/table/tbody')
        dates = month.find_elements(By.TAG_NAME, 'td')
        ava_date_btn = None
        for date in dates:
            if date.get_attribute('class') == ' undefined':
                ava_date_btn = date.find_element(By.TAG_NAME, "a")
                break
        ava_date_btn.click()

        # Select time of the date:
        select_elem = driver.find_element(By.ID, 'appointments_consulate_appointment_time')
        select_elem.click()
        options = select_elem.find_elements(By.TAG_NAME, 'option')
        options[len(options)-1].click()

        # Click "Reschedule"
        driver.find_element(By.XPATH, '/html/body/div[4]/main/div[4]/div/div/form/div[2]/fieldset/ol/li/input').click()
        try:
            confirm = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div/div/a[2]'))
            )
        finally:
            driver.implicitly_wait(0.05)
            confirm.click()
        sleep(5)
        return avalible_in_months
    else:
        driver.close()
        return -1

if __name__ == "__main__":
    # Use a dictionary found_slots to record the (nearest avalible month: times_found) pairs
    found_slots = {}
    no_slot_count = 0
    found_slot_count = 0
    result = -1
    attempt_count = 0
    while result == -1 or -2 or -3:
        try:
            # result =:
            # -1 if a slot is found but longer than the user-defined MAX_WAIT_MONTH;
            # -2 if no slot is avalible;
            # -3 if there's an error
            # any positive integer if a slot is booked
            result = attempt(email=USER_EMAIL, pw=USER_PASSWORD, wait=MAX_WAIT_MONTH, slots=found_slots)
        except:
            result = -3
        attempt_count += 1
        os.system('clear')
        print("Attempt: {}".format(attempt_count))
        if result == -1:
            found_slot_count += 1
            print("Slot found but wait time longer than desired")
            print("Previously found: {}".format(found_slots))
            print("No slot: {} Found slot: {}".format(no_slot_count, found_slot_count))
            print("Retrying in {} seconds".format(FOUND_SLOT_RETRY_DELAY))
            print("#################################")
            sleep(FOUND_SLOT_RETRY_DELAY)
        elif result == -2:
            no_slot_count += 1
            print("No slot currently avalible")
            print("Previously found: {}".format(found_slots))
            print("No slot: {} Found slot: {}".format(no_slot_count, found_slot_count))
            print("Retrying in {} seconds".format(NO_SLOT_RETRY_DELAY))
            print("#################################")
            sleep(NO_SLOT_RETRY_DELAY)
        elif result == -3:
            print("ERROR!!! Please check user email/password or network")
            print("#################################")
        else:
            print("SUCCEED!!! Booked a slot in {} months".format(result))
            break
