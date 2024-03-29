from django.db import models


class MoltinToken(models.Model):
    access_token = models.CharField(max_length=200)
    token_creation_time = models.DateTimeField(blank=True, null=True)
    token_end_time = models.DateTimeField(blank=True, null=True)
    active_token = models.BooleanField()
    def __str__(self):
        return self.access_token


class TelegramUser(models.Model):
    chat_id = models.CharField(max_length=200)
    next_state = models.CharField(max_length=200)
    address_pizzeria = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.chat_id
