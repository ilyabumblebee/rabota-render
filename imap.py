import imaplib
import email
from email.header import decode_header
import re

def get_confirmation_url_imap(imap_url, email_address, password):
    # Connect to an IMAP server
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(email_address, password)
    mail.select('inbox')

    # Search for emails with the specific subject
    status, messages = mail.search(None, '(SUBJECT "Activate your Render account")')
    if status != 'OK':
        return None

    for num in messages[0].split():
        # Fetch each email's content
        status, data = mail.fetch(num, '(RFC822)')
        if status != 'OK':
            return None

        # Parse email content
        msg = email.message_from_bytes(data[0][1])
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    bytes_payload = part.get_payload(decode=True)
                    message_content = bytes_payload.decode()
                    # Use regular expression to find the URL
                    urls = re.findall(r'https://click\.pstmrk\.it/3ts/[^\s"]+', message_content)
                    if urls:
                        return urls[0]  # Return the first URL found
        else:
            # For non-multipart emails
            content_type = msg.get_content_type()
            if content_type == 'text/plain':
                message_content = msg.get_payload(decode=True).decode()
                urls = re.findall(r'https://click\.pstmrk\.it/3ts/[^\s"]+', message_content)
                if urls:
                    return urls[0]

    return None
