# US Visa Rescheduler for Canada

A simple Python script for making US visa interview appointments in Canada

## Setup

Make sure you have booked an appointment on https://ais.usvisa-info.com/en-ca/.

Install dependencies (Python3 is required):

```sh
pip install -r requirements.txt
```

Modify `settings.py` as per the instructions within the script:

```python3
USER_EMAIL = "name@gmail.com"
USER_PASSWORD = "yourpassword"
EARLIEST_ACCEPTABLE_DATE = "2024-01-01"  # this is now only used in detecting
LATEST_ACCEPTABLE_DATE = "2024-03-14"
USER_CONSULATE = "Toronto"
```

### Find a slot and book it automatically

```sh
python reschedule.py
```

See the script in action. Once you're satisfied with its functionality, set `TEST_MODE` to `False` in `settings.py`. For a headless operation, you can also set `SHOW_GUI` to `False` and allow the script to run unattended.

Note `detect_and_notify.py` is no longer maintained.

## Service instructions

```sh
mkdir -p logs
sudo cp usvisa-rescheduler.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable usvisa-rescheduler
sudo systemctl start usvisa-rescheduler

python reschedule.py > logs/rescheduler.log 2>&1 &
```

## VM without Service

```sh
sudo apt update
sudo apt install python3-pip python3-selenium chromium-browser chromium-chromedriver screen

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

sudo mkdir -p /var/log/usvisa-rescheduler
sudo chown -R root:root /var/log/usvisa-rescheduler
sudo chmod 755 /var/log/usvisa-rescheduler

cd /root
git clone <your-repo-url> usvisa-ca
cd usvisa-ca

screen -L -Logfile /var/log/usvisa-rescheduler/rescheduler.log -S visa-rescheduler

python3 reschedule.py
```

## Local in background

```sh
brew install screen
screen -S visa-rescheduler
python3 reschedule.py
```

To manage the screen session:
Detach from screen: Ctrl+A then D
Reattach to screen: screen -r visa-rescheduler
List screen sessions: screen -ls
Kill screen session: Ctrl+A then K

## Caution

It may not always be feasible to reschedule an appointment multiple times. Therefore, it's crucial to use `TEST_MODE = True` for testing purposes and ensure the `LATEST_ACCEPTABLE_DATE` is genuinely acceptable to you.

Consulates other than Toronto and Vancouver are not tested.

## Contribution

Please feel free to report issues. PRs are welcomed and greatly appreciated!

One improvement I'm interested in is rewriting `legacy_rescheduler` using `requests`.

## Special thanks

Huge thanks to [@jywyq](https://github.com/jywyq) for adding the Gmail notification feature.

Huge thanks to [@bsingh-kpt](https://github.com/bsingh-kpt) for (finally!) fixing the `legacy_rescheduler` in Mar 2025.

Thanks to [@trungnguyen21](https://github.com/trungnguyen21) and [@saroopskesav](https://github.com/saroopskesav) for helping with the consulate numbers in other cities.

## Disclaimer

This script is provided as-is for the purpose of assisting individuals in rescheduling appointments. While it has been developed with care and with the intention of being helpful, it comes with no guarantees or warranties of any kind, either expressed or implied. By using this script, you acknowledge and agree that you are doing so at your own risk. The author(s) or contributor(s) of this script shall not be held liable for any direct or indirect damages that arise from its use. Please ensure that you understand the actions performed by this script before running it, and consider the ethical and legal implications of its use in your context.
