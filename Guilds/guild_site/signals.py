from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, post_delete, pre_delete, m2m_changed, pre_save
from django.template.loader import render_to_string
from django.dispatch import receiver  # импортируем нужный декоратор
import re
# from bbw.tasks import send_single_email
from .models import Post, SiteUser, AuthCode, Category, STRIP_HTML_TAGS, Reply
from .tasks import send_single_email

REPLY_SUCCESS_TEXT = 'принял ваш отклик. Радостно!'
REPLY_FAIL_TEXT = 'октлонил ваш отклик. Горестно!'

def has_group(user, group_id):
    return user.groups.filter(pk=group_id).exists()

@receiver(post_save, sender=User)
def create_siteuser(sender, instance: User, created=False, **kwargs):
    if created:
        instance.groups.add(1)
        instance.save()
        siteuser = SiteUser.objects.create(user=instance, username=instance.username)


@receiver(post_save, sender=SiteUser)
def generate_code_or_update_permissions(sender, instance: SiteUser, created=False, **kwargs):
    if created:
        code = AuthCode.objects.create(user=instance)
        return
    if instance.is_activated and not has_group(instance.user, 3):  # user is activated
        instance.user.groups.add(3)  # add to confirmed users
        instance.user.groups.remove(1)  # remove from unconfirmed users
    elif not instance.is_activated and has_group(instance.user, 3):  # user got banned, do the reverse
        instance.user.groups.add(1)
        instance.user.groups.remove(3)
    if instance.is_editor and not has_group(instance.user, 2):  # similar story but with editor status
        instance.user.groups.add(2)
    elif not instance.is_activated and not has_group(instance.user, 2):  # user got banned, do the reverse
        instance.user.groups.remove(2)


@receiver(post_save, sender=AuthCode)
def email_code(sender, instance: AuthCode, created=False, **kwargs):
    send_single_email.delay(subject='Код для завершения регистрации на сайте',
                            body=f'Ваш код: {instance.code}',
                            from_email='test@testing.time',
                            to_emails=[instance.user.user.email])


@receiver(post_save, sender=Reply)
def email_on_reply_creation(sender, instance: Reply, created=False, **kwargs):
    if created:  # send e-mail to post creator
        send_single_email.delay(subject=f'{instance.user.username} откликнулся на ваше объявление{instance.post.title[:40]}',
                                body=f'Увидеть свои отклики вы можете по адресу http://127.0.0.1:8000/my_replies\n{instance.body}',
                                from_email='test@testing.time',
                                to_emails=[instance.post.user.user.email])


@receiver(pre_save, sender=Reply)
def email_on_reply_status_change(sender, instance: Reply, **kwargs):
    if instance.id is not None:
        prior_state = Reply.objects.get(id=instance.id)
        if prior_state.approved != instance.approved:
            if instance.approved is None:
                return
            if instance.approved:
                subject = f'{instance.post.user.username} {REPLY_SUCCESS_TEXT}'
            else:
                subject = f'{instance.post.user.username} {REPLY_FAIL_TEXT}'
            send_single_email.delay(
                subject=subject,
                body=f'Ваш отклик:\n{instance.body}',
                from_email='test@testing.time',
                to_emails=[instance.user.user.email])




