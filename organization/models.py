from django.db import models
# from account.models import User


class Organization(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    phone = models.PositiveIntegerField()
    owner = models.OneToOneField(to='account.User', on_delete=models.CASCADE, related_name='owner', null=True)

    def __str__(self):
        return self.name
