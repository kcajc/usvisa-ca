# US Visa Re-scheduler for Canada
An Extremely Simple Python Script for Making US Visa Interview Appointment in Canada
## Setup
Make sure you have booked an appointment on https://ais.usvisa-info.com/en-ca/.

Have Python3 installed and PIP install Selenium and Web Driver Manager:
```
$ pip3 install selenium
$ pip3 install webdriver_manager
```

Modify the following code in the script with instructions in the script:
```
USER_EMAIL = "name@gmail.com"
USER_PASSWORD = "yourpassword"
MAX_WAIT_MONTH = 6
```
Run the script:
```
$ python3 findslot.py
```
## Optimization
Use `FOUND_SLOT_RETRY_DELAY` and `NO_SLOT_RETRY_DELAY` (in seconds) to change the the wait between attempts.
```
FOUND_SLOT_RETRY_DELAY = 180
NO_SLOT_RETRY_DELAY = 180
```

Please note that a shorter delay may result in not finding any avalible slot. 180 seconds is tested to be safe for now.
