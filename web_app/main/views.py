from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import City, PointOfInterest
from scripts.find_similar_pois import find_similar_pois, find_similar_pois_by_image, find_similar_pois_by_image_in_other_cities


def city_list(request):
    cities = City.objects.all()
    return render(request, 'city_list.html', {'cities': cities})

def point_of_interest_list(request, city_id):
    city = get_object_or_404(City, pk=city_id)
    points_of_interest = PointOfInterest.objects.filter(city=city).exclude(image_url__exact='')
    paginator = Paginator(points_of_interest, 100)  # Show 100 points of interest per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'point_of_interest_list.html', {'city': city, 'page_obj': page_obj})

def point_of_interest_detail(request, point_id):
    point = get_object_or_404(PointOfInterest, pk=point_id)
    city_id = point.city.id
    search_method = request.GET.get('search_method', 'default')

    if search_method == 'image':
        similar_pois = find_similar_pois_by_image(city_id, point_id)
    elif search_method == 'other_cities':
        similar_pois = find_similar_pois_by_image_in_other_cities(city_id, point_id)
    else:
        similar_pois = find_similar_pois(city_id, point_id)

    return render(request, 'point_of_interest_detail.html', {
        'point': point,
        'similar_pois': similar_pois,
        'search_method': search_method
    })