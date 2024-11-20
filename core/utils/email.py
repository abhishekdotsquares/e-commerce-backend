from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# from core.config import config
import os 

# Email sending function
async def send_email(to_email: str, subject: str, body: str):
    try:
        # Configure email server (using example settings, update with real credentials)
        smtp = SMTP(os.getenv("SMTP_HOST"), os.getenv("SMTP_PORT"))
        smtp.starttls()
        smtp.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
        
        # Prepare email
        msg = MIMEMultipart()
        msg["From"] = "kashish@dotsquares.com"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        smtp.sendmail("kashish@dotsquares.com", to_email, msg.as_string())
        smtp.quit()
    except Exception as e:
        print(f"Error sending email: {e}")
        raise Exception("Failed to send email.")