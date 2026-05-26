from flask import current_app, render_template_string
from flask_mail import Message


def send_contact_email(mail, data):
    body = f"""
New Contact Form Submission — JK Data Lab
==========================================
Name:    {data.get('name')}
Email:   {data.get('email')}
Company: {data.get('company', 'N/A')}
Service: {data.get('service', 'N/A')}
Budget:  {data.get('budget', 'N/A')}

Message:
{data.get('message')}
"""
    try:
        msg = Message(
            subject=f"New Enquiry from {data.get('name')} — JK Data Lab",
            recipients=[current_app.config['CONTACT_RECEIVER']],
            body=body,
            reply_to=data.get('email'),
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Email send failed: {e}")
        return False
