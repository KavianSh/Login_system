from django.db import models

class FailedLoginAttempt(models.Model):
    ip_address = models.GenericIPAddressField()
    phone_number = models.CharField(max_length=15)
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)

class OTPRequest(models.Model):
    ip_address = models.GenericIPAddressField()
    phone_number = models.CharField(max_length=15)
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)
