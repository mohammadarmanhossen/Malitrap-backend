import asyncio
import os
import sys
import logging
from email import message_from_bytes
from email.policy import default

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SMTP-Server")

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

import django
django.setup()

from asgiref.sync import sync_to_async
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword
from api.models import Inbox, Email, Attachment
from django.core.files.base import ContentFile

def auth_mechanism(server, session, envelope, mechanism, auth_data):
    if mechanism not in ("LOGIN", "PLAIN"):
        return AuthResult(success=False, handled=False)
    if not isinstance(auth_data, LoginPassword):
        return AuthResult(success=False, handled=False)
    
    username = auth_data.login.decode('utf-8') if isinstance(auth_data.login, bytes) else auth_data.login
    password = auth_data.password.decode('utf-8') if isinstance(auth_data.password, bytes) else auth_data.password
    
    try:
        inbox = Inbox.objects.get(smtp_username=username, smtp_password=password)
        session.authenticated_inbox = inbox
        logger.info(f"Authenticated session for inbox: {inbox.name}")
        return AuthResult(success=True)
    except Inbox.DoesNotExist:
        logger.warning(f"Failed authentication attempt for user: {username}")
        return AuthResult(success=False, handled=False)

class MailtrapHandler:
    @sync_to_async
    def handle_message(self, session, envelope):
        mailfrom = envelope.mail_from
        rcpttos = envelope.rcpt_tos
        data = envelope.content

        # Parse the email
        msg = message_from_bytes(data, policy=default)
        subject = msg['subject'] or '(no subject)'

        # Use the authenticated inbox
        inbox = getattr(session, 'authenticated_inbox', None)
        if not inbox:
            logger.error("Unauthenticated email received. Dropping.")
            return '530 Authentication required'

        recipient = rcpttos[0] if rcpttos else ''

        # Extract body
        body_text = ''
        body_html = ''
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    charset = part.get_content_charset('utf-8') or 'utf-8'
                    body_text += part.get_payload(decode=True).decode(charset, errors='replace')
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    charset = part.get_content_charset('utf-8') or 'utf-8'
                    body_html += part.get_payload(decode=True).decode(charset, errors='replace')
        else:
            content_type = msg.get_content_type()
            charset = msg.get_content_charset('utf-8') or 'utf-8'
            payload = msg.get_payload(decode=True).decode(charset, errors='replace')
            if content_type == "text/html":
                body_html = payload
            else:
                body_text = payload

        # Create email record
        email_record = Email.objects.create(
            inbox=inbox,
            sender=mailfrom,
            recipient=recipient,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            raw_source=data.decode('utf-8', errors='replace')
        )

        # Handle attachments
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                
                filename = part.get_filename()
                if filename:
                    file_data = part.get_payload(decode=True)
                    content_type = part.get_content_type()
                    
                    attachment = Attachment(
                        email=email_record,
                        filename=filename,
                        content_type=content_type,
                        size=len(file_data)
                    )
                    attachment.file.save(filename, ContentFile(file_data), save=True)

        logger.info(f"Stored email from {mailfrom} for Inbox {inbox.name} (ID: {email_record.id})")
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        return await self.handle_message(session, envelope)

def run_server():
    handler = MailtrapHandler()
    smtp_host = os.environ.get('SMTP_HOST', '127.0.0.1')
    smtp_port = int(os.environ.get('SMTP_PORT', '2525'))
    
    controller = Controller(
        handler, 
        hostname=smtp_host, 
        port=smtp_port, 
        authenticator=auth_mechanism, 
        auth_require_tls=False
    )
    
    logger.info(f"Starting Mailtrap SMTP server on {smtp_host}:{smtp_port}...")
    controller.start()
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Stopping SMTP server...")
    finally:
        controller.stop()

if __name__ == '__main__':
    run_server()
