from django.db import models

# Create your models here.
class Flight(models.Model):
    company = models.CharField(max_length=20)
    price = models.IntegerField()
    departure = models.TimeField()
    arrival = models.TimeField()
    stops = models.IntegerField()