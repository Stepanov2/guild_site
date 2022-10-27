from celery import shared_task
from typing import Union
# import logging
import re

# from django.conf import settings

# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth.models import User
# from django.core.management.base import BaseCommand
# from django_apscheduler.jobstores import DjangoJobStore
# from django_apscheduler.models import DjangoJobExecution
from datetime import datetime, timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
#
# from d5 import get_random_sentences
#
from django.utils import timezone

from guild_site.models import Post, SiteUser, AuthCode, STRIP_HTML_TAGS, Email, MailingList
#
import pytz

# =====

utc = pytz.UTC
POSTS_INTERVAL = 60*60*24*7  # seconds


@shared_task
def hello():
    print('=)' * 10)


@shared_task
def send_single_email(subject: str,
                      to_emails: Union[str, list],
                      from_email: Union[str, None] = 'test@testing.time',
                      body: Union[str, None] = None,
                      html_body: Union[str, None] = None) -> str:
    """Send an email. Will generate body from html_body if needed.
    Despite the name this function will accept a list of recipients.
    But you shouldn't use it this way, (unless you are emailing stuff)
    as it will leak the list of emails to everyone on that list.
    """

    # prep work
    if body is None and html_body is None:
        raise ValueError('This function needs either body or html_body parameter to work!')
    if body is None:  # generate plain-text body from html
        body = re.sub(STRIP_HTML_TAGS, '', html_body).replace('\n\n', '')
    if from_email is None:
        from_email = 'test@testing.time'
    if not isinstance(to_emails, list):  # convert str to list
        to_emails = [to_emails]

    # generating e-mail.
    my_email = EmailMultiAlternatives(subject=subject,
                                          body=body,
                                          from_email=from_email,
                                          to=to_emails)
    if html_body is not None:
        my_email.attach_alternative(html_body, "text/html")
    my_email.send()  # sending e-mail

    return f'Sent a letter "{subject}" to {str(to_emails)}'

@shared_task
def send_mass_email() -> str:
    emails_to_send = Email.objects.filter(finalized=True, sent=False, sending_time__lte=timezone.now())
    if not emails_to_send:
        return 'Nothing to send!'
    else:
        for email in emails_to_send:
            print(f'Found email {email.title}')
            html = render_to_string('email_header.html')
            html += str(email.body).replace('<img src="', '<img src="http://127.0.0.1:8000')
            html += render_to_string('email_footer.html')
            users = email.mailing_list.subscribers.all()
            for user in users:
                send_single_email.delay(subject=email.title,
                                        html_body=html,
                                        from_email='test@testing.time',
                                        to_emails=[user.user.email])
                print(f'PLANNED an email for {user}!')
            email.sent = True
            email.save()

