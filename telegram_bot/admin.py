from django.contrib import admin
from .models import MoltinToken, TelegramUser


@admin.register(MoltinToken)
class MoltinTokenAdmin(admin.ModelAdmin):
    pass


@admin.register(TelegramUser)
class MoltinTokenAdmin(admin.ModelAdmin):
    pass
