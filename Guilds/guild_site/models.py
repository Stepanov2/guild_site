from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.contrib.auth.models import User
import re
from django.utils import timezone

import datetime
from django.urls import reverse_lazy
from django.conf import settings
from random import randint

STRIP_HTML_TAGS = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
# God bless stack overflow!


class BaseModel(models.Model):
    """A dirty little hack to allow PyCharm community edition (and, possibly other IDEs) to correctly resolve
    .objects for models. # God bless stack overflow!
    """

    objects = models.Manager()

    class Meta:
        abstract = True


class SiteUser(BaseModel):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, unique=True)  # copied from auth.user to avoid loading SiteUser.User
    is_editor = models.BooleanField(default=False)            # for every post/comment in template rendering
    date_registered = models.DateTimeField(auto_now_add=True, editable=False)
    is_activated = models.BooleanField(default=False)
    subscription = models.ManyToManyField('MailingList', through='MailingListSubscribers')

    class Meta:
        ordering = ['date_registered']

    def __str__(self):
        return self.username


class MailingList(BaseModel):
    title = models.CharField(max_length=200)
    subscribers = models.ManyToManyField(SiteUser, through='MailingListSubscribers')

    class Meta:
        pass

    def __str__(self):
        return self.title


class MailingListSubscribers(BaseModel):
    """ post_id	INT tag_id	INT"""
    mailing_list = models.ForeignKey(MailingList, on_delete=models.CASCADE)
    site_user = models.ForeignKey(SiteUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['mailing_list', 'site_user']  # you can only subscribe once

    def __str__(self):
        return f'{self.site_user.username} is subscribed to {self.mailing_list.title}'


class Email(BaseModel):
    mailing_list = models.ForeignKey(MailingList, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    finalized = models.BooleanField(default=False)
    sending_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-finalized', 'sending_time']

    def __str__(self):
        return self.title


class AuthCode(BaseModel):
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE)
    code = models.PositiveSmallIntegerField(editable=False)
    expires = models.DateTimeField(editable=False)

    class Meta:
        pass

    def save(self, *args, **kwargs):
        """Generates the code and makes it expire after settings.LOGIN_CODE_TTL seconds. Default:180"""
        delta = getattr(settings, 'LOGIN_CODE_TTL', 180)

        if not self.id:
            self.code = randint(10_000, 65_535)
            self.expires = timezone.now() + timezone.timedelta(seconds=delta)

        return super(AuthCode, self).save(*args, **kwargs)

    @classmethod
    def flush_old_codes(cls):
        # TODO
        pass


class Category(BaseModel):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f'{self.slug}: {self.title}'


class Post(BaseModel):
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = RichTextUploadingField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['category', '-created']),
                   models.Index(fields=['-created']),
                   models.Index(fields=['user'])]

    def __str__(self):
        return f'Post "{self.title}" by user {self.user.username}'


class Reply(BaseModel):
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    body = models.TextField()
    approved = models.BooleanField(null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['post', 'created']),
                   models.Index(fields=['user', '-created']),]

    def __str__(self):
        return f'{self.body[:80]}...'

