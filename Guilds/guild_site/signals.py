from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, post_delete, pre_delete, m2m_changed
from django.template.loader import render_to_string
from django.dispatch import receiver  # импортируем нужный декоратор
import re
# from bbw.tasks import send_single_email
from .models import Post, SiteUser, AuthCode, Category, STRIP_HTML_TAGS
from .tasks import send_single_email


@receiver(post_save, sender=User)
def create_siteuser(sender, instance: User, created=False, **kwargs):
    if created:
        siteuser = SiteUser.objects.create(user=instance, username=instance.username)


@receiver(post_save, sender=SiteUser)
def generate_code(sender, instance: SiteUser, created=False, **kwargs):
    if created:
        code = AuthCode.objects.create(user=instance)


@receiver(post_save, sender=AuthCode)
def email_code(sender, instance: AuthCode, created=False, **kwargs):
    send_single_email.delay(subject='Код для завершения регистрации на сайте',
                            body=f'Ваш код: {instance.code}',
                            from_email='test@testing.time',
                            to_emails=[instance.user.user.email])

