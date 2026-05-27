import resend
from flask import current_app


def send_contact_email(data):
    api_key = current_app.config.get('RESEND_API_KEY')
    if not api_key:
        current_app.logger.warning("RESEND_API_KEY not set — email skipped")
        return False

    body = f"""New Contact Form Submission — JK Data Lab
==========================================
Name:    {data.get('name')}
Email:   {data.get('email')}
Company: {data.get('company') or 'N/A'}
Service: {data.get('service') or 'N/A'}
Budget:  {data.get('budget') or 'N/A'}

Message:
{data.get('message')}
"""
    sender   = current_app.config.get('MAIL_DEFAULT_SENDER', 'kinjal@jkdatalab.com')
    receiver = current_app.config.get('CONTACT_RECEIVER', 'kinjal@jkdatalab.com')

    try:
        resend.api_key = api_key
        resend.Emails.send({
            "from": f"JK Data Lab <{sender}>",
            "to": [receiver],
            "subject": f"New Enquiry from {data.get('name')} — JK Data Lab",
            "text": body,
            "reply_to": data.get('email'),
        })
        return True
    except Exception as e:
        current_app.logger.error(f"Resend email failed: {e}")
        return False
