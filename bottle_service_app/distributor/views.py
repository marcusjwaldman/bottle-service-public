from django.shortcuts import render


def distributor_home(request):
    return render(request, 'distributor/distributor_home.html')
