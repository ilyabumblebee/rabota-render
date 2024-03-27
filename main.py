import os
import re
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from verifyemail import verify_email
from registration import sign_up_user
from imap import get_confirmation_url_imap
from mailtm import get_confirmation_url_mailtm
from hcaptcha_manual import solve_captcha_manual
from hcaptcha_service import solve_captcha_service
from db import get_db_connection, fetch_emails, update_registration_status, append_account

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
services = config['email_services']
imap_url = config.get('imap_url', '')
use_imap = config.get('use_imap', False)
hcaptcha_sitekey = config['hcaptcha_sitekey']
hcaptcha_mode = config.get('hcaptcha_mode', 1)
anticaptcha_apikey = config['anticaptcha_apikey']

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

def main(sitekey, hcaptcha_mode, anticaptcha_apikey, dbname, user, dbpassword, host, port):
    init_conn = get_db_connection(dbname, user, dbpassword, host, port)
    emails = fetch_emails(init_conn, services)
    logging.info("database connection successful")
    init_conn.close()
    for email_pass in emails:
        email, password = email_pass

        while True:
            toggle_airplane_mode()
            session = requests.Session()
            if hcaptcha_mode == 0:
                token = solve_captcha_service(anticaptcha_apikey, sitekey)
            else:
                token = solve_captcha_manual(sitekey)
            prim_conn = get_db_connection(dbname, user, dbpassword, host, port)
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
                    if use_imap:
                        confirmation_url = get_confirmation_url_imap(imap_url, email, password)
                    else:
                        confirmation_url = get_confirmation_url_mailtm(email, password)                    
                    attempts += 1
                if confirmation_url is not None:
                    email_token = re.search(r"token=([^/&]+)", unquote(confirmation_url))
                    if email_token:
                        response = verify_email(session, email_token.group(1))
                    if response.status_code == 200:
                        logging.info(f"registration successful for {email}")
                        status = append_account(prim_conn, email, password)
                        if status == 201:
                            logging.info(f"account for {email} appended successfully")
                    else:
                        logging.error(f"registration error for {email}")

                break

        status = update_registration_status(prim_conn, email)
        if status==201:
            logging.info(f"updated registration status for {email}")
        prim_conn.close()

main(hcaptcha_sitekey, hcaptcha_mode, anticaptcha_apikey, dbname, user, password, host, port)
