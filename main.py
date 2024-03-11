import os
import re
import json
import time
import requests
from faker import Faker
from bs4 import BeautifulSoup
from hcaptcha import solve_captcha
from registration import sign_up_user
from mailtm import get_confirmation_url


# Load configuration from JSON file directly
with open('config.json', 'r') as file:
    config = json.load(file)

# Assign each configuration item to a variable
filename = config['email_file']
hcaptcha_sitekey = config['hcaptcha_sitekey']

fake = Faker()

def extract_emails(filename):
    results = []
    with open(filename, 'r', encoding='utf-8', errors='replace') as file:  # Note the added encoding and errors parameters
        for line in file:
            if re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}:[^\s]+\b').match(line.strip()):
                results.append(line.strip())
    return results

def toggle_airplane_mode():
    print("Toggling airplane mode...")
    os.system("adb shell cmd connectivity airplane-mode enable")
    time.sleep(0.25)
    os.system("adb shell cmd connectivity airplane-mode disable")
    time.sleep(5)

def main(filename, sitekey, extracted):
    for email_pass in extracted:
        email, password = email_pass.split(':')
        name = fake.name()
        
        while True:
            toggle_airplane_mode()

            session = requests.Session()

            token = solve_captcha(sitekey)

            if token:
                code, session = sign_up_user(session, email, token)
            else:
                print("captcha_token not defined")
            if code == 429:
                toggle_airplane_mode()
                continue
            elif code == 500:
                print(f"Skipping account {email} due to server error.")
                break
            elif code == 200:
                time.sleep(10)
                confirmation_url = get_confirmation_url(email, password)
                print(confirmation_url)
                if confirmation_url is not None:
                    response = session.get(confirmation_url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        print(f"Verification successful for {email}")
                    else:
                        print(f"Error following verification URL for {email}")
                break

extracted = extract_emails(filename)
main(filename, hcaptcha_sitekey, extracted)
