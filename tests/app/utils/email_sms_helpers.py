import hashlib
import random
import re
import string
import time

import requests
from bs4 import BeautifulSoup

from tests.app.pages.base.settings import Settings
from tests.app.utils.timers import TimeOut


class EmailAndSmsFetchCode(Settings):
    def create_mail_tm_inbox(self, logger=None):
        """Create a Mail.tm inbox with custom format:
        testqa<5-6 digits>_<randomstring>@<domain>
        Returns: (email_address, password)
        """
        base_url = "https://api.mail.tm"

        # Get available domains
        try:
            domains_resp = requests.get(f"{base_url}/domains")
            domains_resp.raise_for_status()
            domains = domains_resp.json()["hydra:member"]
            if not domains:
                raise ValueError("No domains available from Mail.tm")
            domain = domains[0]["domain"]
            if logger:
                logger.info(f"Selected domain: {domain}")
        except Exception as e:
            if logger:
                logger.error(f"Failed to fetch domains: {str(e)}")
            raise

        # Generate custom email format
        digits = "".join(random.choices(string.digits, k=random.choice([5, 6])))
        rand_str = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
        username = f"testqa{digits}_{rand_str}"
        email_address = f"{username}@{domain}"

        # Generate password (random 12 chars)
        password = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        if logger:
            logger.info(f"Generated email: {email_address}")

        # Create inbox
        try:
            create_payload = {"address": email_address, "password": password}
            create_resp = requests.post(f"{base_url}/accounts", json=create_payload)
            create_resp.raise_for_status()
            account_id = create_resp.json()["id"]
            if logger:
                logger.info(f"Created inbox with ID: {account_id}")
            return email_address, password
        except Exception as e:
            if logger:
                logger.error(f"Failed to create inbox: {str(e)}")
            raise

    def get_otp_from_mail_tm(self, email_address, password, timeout=90, logger=None):
        """Fetch OTP from the latest email sent to the provided Mail.tm email address"""
        base_url = "https://api.mail.tm"

        # Authenticate to get token
        try:
            token_payload = {"address": email_address, "password": password}
            token_resp = requests.post(f"{base_url}/token", json=token_payload)
            token_resp.raise_for_status()
            token = token_resp.json()["token"]
            headers = {"Authorization": f"Bearer {token}"}
            logger.info(f"Authenticated for inbox: {email_address}")
        except Exception as e:
            logger.error(f"Failed to authenticate for {email_address}: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
            raise ValueError(
                f"Authentication failed for {email_address}. Check email and password."
            )

        # Initial delay to allow email delivery
        logger.debug("Waiting 5 seconds before polling to allow email delivery...")
        time.sleep(TimeOut.FIVE_SECONDS)

        # Poll for emails and extract OTP from the latest email
        start_time = time.time()
        seen_ids = set()  # Track processed email IDs
        while time.time() - start_time < timeout:
            try:
                # Retry API call up to 3 times
                for attempt in range(3):
                    try:
                        messages_resp = requests.get(
                            f"{base_url}/messages?page=1", headers=headers, timeout=10
                        )
                        messages_resp.raise_for_status()
                        break
                    except requests.RequestException as e:
                        logger.warning(f"API request failed (attempt {attempt + 1}/3): {str(e)}")
                        if attempt == 2:
                            raise
                        time.sleep(TimeOut.TWO_SECONDS)

                messages = messages_resp.json()["hydra:member"]
                if not messages:
                    logger.debug(" No emails yet")
                    time.sleep(5)
                    continue

                logger.info(f" Found {len(messages)} emails in inbox")
                new_emails_processed = False  # Track if we process any new emails

                # Process emails (newest first)
                for msg in messages:
                    msg_id = msg.get("id")
                    if not msg_id or msg_id in seen_ids:
                        continue
                    seen_ids.add(msg_id)
                    new_emails_processed = True

                    sender = msg.get("from", {}).get("address", "Unknown sender")
                    subject = msg.get("subject", "No subject")
                    logger.info(
                        f"Processing email ID: {msg_id}, From: {sender}, Subject: {subject}"
                    )

                    # Fetch full message
                    logger.info(f" Processing email ID: {msg_id}")
                    msg_resp = requests.get(f"{base_url}/messages/{msg_id}", headers=headers)
                    msg_resp.raise_for_status()
                    msg_data = msg_resp.json()

                    # Check text and html bodies
                    bodies = [msg_data.get("text", ""), msg_data.get("html", "")]
                    for body in bodies:
                        if not body:
                            continue
                        # Clean HTML to plain text if needed
                        if "<" in body and ">" in body:
                            logger.debug("Parsing HTML body to text")
                            clean_body = BeautifulSoup(body, "html.parser").get_text(
                                separator=" ", strip=True
                            )
                        else:
                            clean_body = body

                        # Log full body for debugging
                        logger.debug(f"Email body (cleaned): {clean_body}")

                        # Try multiple regex patterns for OTP
                        patterns = [
                            r"(\d{6})\s*is\s*(?:your|Your)\s*(?:GETTR\s*)?verification\s*code",
                            r"Code:?\s*(\d{6})",
                            r"Verification\s*Code:?\s*(\d{6})",
                            r"Your\s*code\s*is\s*(\d{6})",
                            r"(\d{6})",  # Broad fallback for any 6-digit code
                        ]
                        for pattern in patterns:
                            match = re.search(pattern, clean_body, re.IGNORECASE)
                            if match:
                                otp = match.group(1)
                                if otp != "000000":
                                    logger.info(f" Valid OTP found: {otp}")
                                    return otp

                        # Fallback: find any 6-digit code
                        fallbacks = re.findall(r"\b\d{6}\b", clean_body)
                        for candidate in fallbacks:
                            if candidate != "000000":
                                logger.info(f" Valid OTP found (fallback): {candidate}")
                                return candidate

                    logger.warning(" No valid OTP found in email ID: {msg_id}")

                if not new_emails_processed:
                    logger.warning(" No new emails to process; all emails checked are processed")
                logger.debug(" Waiting for new emails...")
                time.sleep(5)
            except Exception as e:
                logger.error(f" Error processing emails: {str(e)}")
                import traceback

                logger.error(traceback.format_exc())
                time.sleep(5)

        raise TimeoutError(f" No valid OTP found in inbox {email_address} within {timeout}s")

    def get_otp_from_anonymsms(self, phone_number, logger, timeout=45):
        """
        Fetch OTP from the latest SMS sent to the provided temporary phone number on AnonymSMS.
        Works with the current table layout.
        """

        if not isinstance(phone_number, str):
            raise ValueError("phone_number must be a string")

        phone_number = phone_number.replace("+", "")
        if len(phone_number) == 10 and phone_number.isdigit():
            phone_number = "1" + phone_number

        url = f"https://anonymsms.com/number/{phone_number}/"

        def fetch_messages():
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
            except Exception as e:
                if logger:
                    logger.error(f" Failed to fetch page: {str(e)}")
                return []

            soup = BeautifulSoup(resp.text, "html.parser")

            # Current layout: messages in a <table> with <tr> and <td> for from, text, date
            table = soup.find("table")
            if not table:
                return []

            messages = []
            for row in table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) == 3:
                    sender = cols[0].get_text(strip=True)
                    text = cols[1].get_text(strip=True)
                    date = cols[2].get_text(strip=True)
                    messages.append((sender, text, date))
            return messages

        seen_hashes = {hashlib.sha256(msg[1].encode()).hexdigest() for msg in fetch_messages()}

        start_time = time.time()
        while time.time() - start_time < timeout:
            messages = fetch_messages()
            for sender, text, date in messages:
                msg_hash = hashlib.sha256(text.encode()).hexdigest()
                if msg_hash in seen_hashes:
                    continue
                seen_hashes.add(msg_hash)

                if logger:
                    logger.info(f" New SMS from {sender}: {text}")

                # OTP extraction patterns (prioritized for GETTR)
                patterns = [
                    r"GETTR\s*code:\s*(\d{6})",
                    r"(\d{6})\s*is\s*your",
                    r"Code:?\s*(\d{6})",
                    r"(\d{6})",
                ]
                for p in patterns:
                    m = re.search(p, text, re.IGNORECASE)
                    if m:
                        otp = m.group(1)
                        if logger:
                            logger.info(f" OTP found: {otp}")
                        return otp

            if logger:
                logger.debug(" Waiting for new SMS...")
            time.sleep(5)

        raise TimeoutError(f" No OTP found for {phone_number} in {timeout}s")
