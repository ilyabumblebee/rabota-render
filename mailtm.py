import requests
import re


def get_confirmation_url(email, password):
    def get_auth_token():
        url = "https://api.mail.tm/token"
        payload = {"address": email, "password": password}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        return response.json()['token'] if response.status_code == 200 else None

    def get_messages(token):
        url = "https://api.mail.tm/messages"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        return response.json()['hydra:member'] if response.status_code == 200 else []

    def find_message_id_by_subject(messages):
        for message in messages:
            if message['subject'] == "Activate your Render account":
                return message['id']
        return None

    def get_message_by_id(token, message_id):
        url = f"https://api.mail.tm/messages/{message_id}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else None

    token = get_auth_token()
    if not token:
        return None

    messages = get_messages(token)
    message_id = find_message_id_by_subject(messages)
    if not message_id:
        return None

    message = get_message_by_id(token, message_id)
    if not message:
        return None

    message_content = message.get('text') or message.get('html')
    if not message_content:
        return None

    urls = re.findall(r'https://click\.pstmrk\.it/3ts/[^\s"]+', message_content)
    return urls[0] if urls else None
