import os
import re
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from hcaptcha import solve_captcha
from verifyemail import verify_email
from registration import sign_up_user
from mailtm import get_confirmation_url
from db import get_db_connection, fetch_emails, update_registration_status

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

with open('config.json', 'r') as file:
    config = json.load(file)

dbname = config['dbname']
user = config['user']
password = config['password']
host = config['host']
port = config['port']

service = config['email_service']

hcaptcha_sitekey = config['hcaptcha_sitekey']

def extract_emails(filename):
    results = []
    with open(filename, 'r', encoding='utf-8', errors='replace') as file:
        for line in file:
            if re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}:[^\s]+\b').match(line.strip()):
                results.append(line.strip())
    return results

def toggle_airplane_mode():
    os.system("adb shell cmd connectivity airplane-mode enable")
    time.sleep(0.25)
    os.system("adb shell cmd connectivity airplane-mode disable")
    time.sleep(5)
    logging.info("airplane mode toggled successfully...")

def main(filename, sitekey, conn):
    emails = fetch_emails(conn, service)
    for email_pass in emails:
        email, password = email_pass

        while True:
            toggle_airplane_mode()
            session = requests.Session()
            token = solve_captcha(sitekey)
            if token:
                code, session = sign_up_user(session, email, password, token)
            else:
                break
            if code == 429:
                logging.error(f"registration error for {email}")
                break
            elif code == 200:
                attempts = 0
                confirmation_url = None
                while confirmation_url is None and attempts < 10:
                    time.sleep(10)
                    confirmation_url = get_confirmation_url(email, password)
                    attempts += 1
                if confirmation_url is not None:
                    email_token = re.search(r"token=([^/&]+)", unquote(confirmation_url))
                    if email_token:
                        response = verify_email(session, email_token.group(1))
                    if response.status_code == 200:
                        logging.info(f"registration successful for {email}")
                    else:
                        logging.error(f"registration error for {email}")

                update_registration_status(conn, email)
                logging.info(f"updated registration status for {email}")
                break

conn = get_db_connection(dbname, user, password, host, port)
main(filename, hcaptcha_sitekey, conn)
