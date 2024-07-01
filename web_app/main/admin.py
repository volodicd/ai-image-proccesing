from django.contrib import admin
from .models import City, PointOfInterest


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(PointOfInterest)
class PointOfInterestAdmin(admin.ModelAdmin):
    ist_display = ('id', 'title', 'description', 'image_url', 'city')

