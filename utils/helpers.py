import time
import requests
import re

def fetch_emails_from_mailslurp(logger, list_url, headers, timeout=30):
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            params = {"page": 0, "size": 10, "sort": "DESC"}
            resp = requests.get(list_url, headers=headers, params=params)
            resp.raise_for_status()

            response_data = resp.json()

            if "content" not in response_data:
                logger.warning("⚠️ Unexpected API response format. Trying alternative parsing...")
                emails = response_data
            else:
                emails = response_data["content"]

            if not emails:
                logger.debug(" No emails in inbox")
                time.sleep(3)
                continue

            logger.info(f"Found {len(emails)} emails in inbox")
            return emails  # Optional, but useful

        except requests.RequestException as e:
            logger.error(f"Error fetching emails: {e}")
            time.sleep(3)

def extract_code_from_email_body(self, bodies):
    """
    Extract a 6-digit OTP code from given email bodies.
    Returns the OTP as a string if found, otherwise None.
    """
    for body in bodies:
        if not body:
            continue

        match = re.search(
            r'(\d{6})\s*is\s*(?:your|Your)\s*(?:GETTR\s*)?verification\s*code',
            body
        )
        if match:
            otp = match.group(1)
            if otp != "000000":
                self.logger.info(f"✅ Valid OTP found: {otp}")
                return otp

        # Fallback: any 6-digit number
        fallbacks = re.findall(r'\b\d{6}\b', body)
        for candidate in fallbacks:
            if candidate != "000000":
                self.logger.info(f"✅ Valid OTP found (fallback): {candidate}")
                return candidate

    self.logger.warning("⚠️ No valid OTP found in email")
    return None



