from django.apps import AppConfig


class GuildSiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'guild_site'

    def ready(self):
        import guild_site.signals