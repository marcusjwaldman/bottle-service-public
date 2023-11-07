from django.shortcuts import render


def restaurant_home(request):
    return render(request, 'restaurant/restaurant_home.html')
