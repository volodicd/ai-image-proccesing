from django.db import models

class City(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'cities'

    def __str__(self):
        return self.name

class PointOfInterest(models.Model):
    id = models.AutoField(primary_key=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='points_of_interest')
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.TextField()

    class Meta:
        db_table = 'points_of_interest'

    def __str__(self):
        return self.title
