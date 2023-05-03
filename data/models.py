from django.db import models


# Create your models here.
class CustomerKeys(models.Model):
    customer_name = models.CharField(max_length=100)
    google_docs = models.CharField(max_length=100, null=True, blank=True)
    sfkb_user_name = models.CharField(max_length=100, null=True, blank=True)
    sfkb_password = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.customer_name
