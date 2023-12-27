import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up the message
msg = MIMEMultipart()
msg['From'] = 'name@email.com'
msg['To'] = 'name@email.com'
msg['Subject'] = 'Test Email'

body = 'Body of the email'
msg.attach(MIMEText(body, 'plain'))

# Connect to the SMTP server
smtp_server = 'smtp.gmail.com'  # Replace with your SMTP server address
smtp_port = 587  # Replace with your SMTP server port
smtp_username = 'your@email.com'  # Replace with your SMTP username
smtp_password = 'GOOGLE_APP_PASS'  # Replace with your SMTP password

server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()
server.login(smtp_username, smtp_password)

# Send the message
text = msg.as_string()
server.sendmail(msg['From'], msg['To'], text)
server.quit()
