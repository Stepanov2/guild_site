from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Category)
admin.site.register(SiteUser)
admin.site.register(Post)
admin.site.register(MailingList)
admin.site.register(Email)
admin.site.register(Reply)
