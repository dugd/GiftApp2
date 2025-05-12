from abc import ABC, abstractmethod

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.core.config import get_settings

settings = get_settings()


class MailSender(ABC):
    @abstractmethod
    def send_mail(self, to: str, subject: str, html_content: str) -> None:
        ...


class SendgridMailSender(MailSender):
    def __init__(self):
        self._client = SendGridAPIClient(settings.MAIL_SENDGRID_API_KEY)
        self._from_email = settings.MAIL_SENDER_EMAIL

    def send_mail(self, to: str, subject: str, html_content: str) -> None:
        message = Mail(
            from_email=self._from_email,
            to_emails=to,
            subject=subject,
            html_content=html_content,
        )
        self._client.send(message)

# ---

from dataclasses import dataclass
from typing import Dict, Any

from app.core.settings import jinja_env

@dataclass
class EmailData:
    html_content: str
    subject: str


async def render_email(template_name: str, context: Dict[str, Any]) -> str:
    html = await jinja_env.get_template(f"{template_name}").render_async(**context)
    return html


async def generate_activate_account_email(email_to: str, token: str) -> EmailData:
    app_name = settings.APP_NAME
    link = f"google.com/activate?token={token}"
    subject = f"{app_name} - Activate Account"
    html_content = await render_email(
        template_name="activate_account.html",
        context={
            "app_name": app_name,
            "username": email_to,
            "link": link,

        }
    )
    return EmailData(
        html_content=html_content,
        subject=subject,
    )


async def generate_reset_password_email(email_to: str, token: str) -> EmailData:
    app_name = settings.APP_NAME
    link = f"google.com/reset-password?token={token}"
    subject = f"{app_name} - Reset Password"
    html_content = await render_email(
        template_name="activate_account.html",
        context={
            "app_name": app_name,
            "username": email_to,
            "link": link,
        }
    )
    return EmailData(
        html_content=html_content,
        subject=subject,
    )
