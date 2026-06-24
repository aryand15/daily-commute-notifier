"""Module that handles SMS messaging."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mms(sender_email, sender_password, recipient_email, message_body):
    """
    Send an email-to-SMS/MMS message via Gmail SMTP.

    Connects to Gmail's SMTP server using TLS,
    authenticates using the provided email & password, and sends a multipart
    email message to an SMS/MMS gateway or email recipient.

    Args:
        sender_email (str): Email address used to send the message.
        sender_password (str): App password or SMTP authentication password.
        recipient_email (str): Destination email or SMS/MMS gateway address.
        message_body (str): Plain-text message content.

    Raises:
        smtplib.SMTPException: If any SMTP-related error occurs during
            connection, authentication, or sending.
        Exception: For unexpected errors outside SMTP handling.
    """
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = "Morning Commute + Weather Notification"
    msg.attach(MIMEText(message_body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

    except smtplib.SMTPException:
        raise