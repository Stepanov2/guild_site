from django.contrib import admin
from .models import *
# Register your models here.


class SubscriptionsAdminInline(admin.TabularInline):
    model = SiteUser.subscription.through
    extra = 1


def send_in_1(modeladmin, request, queryset):

    queryset.update(finalized=True, sending_time=timezone.now() + timezone.timedelta(minutes=1))


def send_in_5(modeladmin, request, queryset):

    queryset.update(finalized=True, sending_time=timezone.now() + timezone.timedelta(minutes=5))


def send_in_30(modeladmin, request, queryset):

    queryset.update(finalized=True, sending_time=timezone.now() + timezone.timedelta(minutes=30))


send_in_1.short_description = 'Финализировать и запланировать отправку через 1 минуту.'
send_in_5.short_description = 'Финализировать и запланировать отправку через 5 минут.'
send_in_30.short_description = 'Финализировать и запланировать отправку через 30 минут.'


@admin.register(SiteUser)
class SiteUserAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    list_display = ('pk', 'username',
                    'is_activated', 'is_editor', 'date_registered')
    search_fields = ('username', 'user__email')
    list_display_links = ('username',)
    inlines = (SubscriptionsAdminInline,)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    actions = [send_in_1, send_in_5, send_in_30]
    list_display = ('title', 'mailing_list', 'finalized', 'sending_time', 'sent')


admin.site.register(Category)
# admin.site.register(SiteUser)
admin.site.register(Post)
admin.site.register(MailingList)
# admin.site.register(Email)
admin.site.register(Reply)
