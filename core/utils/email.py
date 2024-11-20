from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email sending function
async def send_email(to_email: str, subject: str, body: str):
    try:
        # Configure email server (using example settings, update with real credentials)
        smtp = SMTP("smtp.example.com", 587)
        smtp.starttls()
        smtp.login("your_email@example.com", "your_password")
        
        # Prepare email
        msg = MIMEMultipart()
        msg["From"] = "your_email@example.com"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        smtp.sendmail("your_email@example.com", to_email, msg.as_string())
        smtp.quit()
    except Exception as e:
        print(f"Error sending email: {e}")
        raise Exception("Failed to send email.")